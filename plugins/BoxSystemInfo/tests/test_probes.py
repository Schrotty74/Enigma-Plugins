"""Mocked tests for read-only system information probes."""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/probes.py'
spec = importlib.util.spec_from_file_location('probes', str(SOURCE))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class ProbeTests(unittest.TestCase):
    def test_cpu_ranges_and_sysfs_frequencies_load(self):
        files = {
            '/sys/devices/system/cpu/online': '0-2,5\n',
            '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq': '1200000',
            '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq': '1800000',
            '/proc/loadavg': '0.12 0.34 0.56 1/99 1234',
        }
        with patch.object(M, '_read', side_effect=lambda path: files.get(path, '')):
            self.assertEqual(M.cpu_info(), [('Kerne', '4'), ('Aktueller Takt', '1200 MHz'),
                                            ('Maximaler Takt', '1800 MHz'),
                                            ('Systemlast (1/5/15 Min.)', '0.12, 0.34, 0.56')])

    def test_cpu_fallback_proc_count_and_unavailable_fields(self):
        def read(path):
            if path == '/proc/cpuinfo':
                return 'processor : 0\nprocessor : 1\ncpu MHz : 900.0\n'
            return ''
        with patch.object(M, '_read', side_effect=read):
            rows = dict(M.cpu_info())
        self.assertEqual(rows['Kerne'], '2')
        self.assertEqual(rows['Aktueller Takt'], '900 MHz')
        self.assertEqual(rows['Maximaler Takt'], M.UNAVAILABLE)
        self.assertEqual(rows['Systemlast (1/5/15 Min.)'], M.UNAVAILABLE)

    def test_network_skips_loopback_and_uses_sysfs_only(self):
        def read(path):
            return {'/sys/class/net/eth0/carrier': '1', '/sys/class/net/eth0/operstate': 'up',
                    '/sys/class/net/eth0/speed': '1000', '/sys/class/net/wlan0/carrier': '0',
                    '/sys/class/net/wlan0/operstate': 'down', '/sys/class/net/wlan0/speed': '-1'}.get(path, '')
        def exists(path):
            return path.endswith('/wlan0/wireless') or path.endswith('/eth0/device')
        with patch.object(M, '_read', side_effect=read), patch.object(M.os, 'listdir', return_value=['lo', 'wlan0', 'eth0']), patch.object(M.os.path, 'exists', side_effect=exists):
            self.assertEqual(M.network_info(), [('eth0', 'LAN · Verbunden · 1000 Mbit/s'),
                                                ('wlan0', 'WLAN · Getrennt · Nicht verfügbar')])

    def test_network_missing_sysfs_reports_unavailable(self):
        with patch.object(M.os, 'listdir', side_effect=OSError()):
            self.assertEqual(M.network_info(), [('Netzwerk', M.UNAVAILABLE)])

    def test_tuner_optional_api_absence_is_unavailable(self):
        with patch.dict(sys.modules, {'Components': None, 'Components.NimManager': None}):
            rows = dict(M.tuner_info(types.SimpleNamespace(nav=types.SimpleNamespace())))
        self.assertEqual(rows['Konfigurierte Tuner'], M.UNAVAILABLE)
        self.assertEqual(rows['Laufende Aufnahmen'], M.UNAVAILABLE)
        self.assertEqual(rows['Tunerbelegung'], M.UNAVAILABLE)

    def test_tuner_configured_slots_and_recording_occupancy(self):
        nim = types.ModuleType('Components.NimManager')
        nim.nimmanager = types.SimpleNamespace(nim_slots=[
            types.SimpleNamespace(friendly_full_description='Tuner A', getSlotType=lambda: 'DVB-S2'),
            types.SimpleNamespace(friendly_full_description='Tuner B', getSlotType=lambda: 'DVB-T2')])
        class Frontend:
            def __init__(self, number): self.number = number
            def getAll(self, *args): return [{'tuner_number': self.number}]
        class Service:
            def frontendInfo(self): return Frontend(0)
        class RecordService:
            def frontendInfo(self): return Frontend(1)
        nav = types.SimpleNamespace(getCurrentService=lambda: Service(), getRecordings=lambda *args: [RecordService()])
        with patch.dict(sys.modules, {'Components': types.ModuleType('Components'), 'Components.NimManager': nim}):
            rows = M.tuner_info(types.SimpleNamespace(nav=nav))
        self.assertEqual(rows, [('Tuner-Frontends', '2'), ('Laufende Aufnahmen', 'Nicht unterscheidbar'),
                                ('Tuner 0', 'Tuner A (DVB-S2) · Aktiv'),
                                ('Tuner 1', 'Tuner B (DVB-T2) · Aktiv')])

    def test_cpufreq_low_khz_is_converted_and_max_is_not_current(self):
        files = {'/sys/devices/system/cpu/online': '0',
                 '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq': '96000',
                 '/proc/cpuinfo': 'cpu MHz : 96.0\n',
                 '/proc/loadavg': ''}
        with patch.object(M, '_read', side_effect=lambda path: files.get(path, '')):
            rows = dict(M.cpu_info())
        self.assertEqual(rows['Aktueller Takt'], '96 MHz')
        self.assertEqual(rows['Maximaler Takt'], M.UNAVAILABLE)

    def test_invalid_negative_cpu_ids_fall_back_to_proc(self):
        self.assertEqual(M._cpu_ids('-1,0'), set())

    def test_unknown_tuners_are_not_reported_free(self):
        nim = types.ModuleType('Components.NimManager')
        nim.nimmanager = types.SimpleNamespace(nim_slots=[
            types.SimpleNamespace(slot=4, friendly_full_description='Long tuner label ignored',
                                  name='Tuner Four', getSlotType=lambda: 'DVB-S2'),
            types.SimpleNamespace(slot=7, name='Unused', getSlotType=lambda: None)])
        nav = types.SimpleNamespace(getCurrentService=lambda: None, getRecordings=lambda *args: [])
        with patch.dict(sys.modules, {'Components': types.ModuleType('Components'), 'Components.NimManager': nim}):
            rows = M.tuner_info(types.SimpleNamespace(nav=nav))
        self.assertEqual(rows, [('Tuner-Frontends', '1'), ('Laufende Aufnahmen', 'Nicht unterscheidbar'),
                                ('Tuner 4', 'Tuner Four (DVB-S2) · Keine aktive Nutzung erkannt')])

    def test_real_recording_filter_counts_and_tracks_frontend(self):
        enigma = types.ModuleType('enigma')
        enigma.pNavigation = types.SimpleNamespace(isRealRecording=17)
        class Frontend:
            def getAll(self, *args): return [{'tuner_number': 3}]
        class RecordService:
            def frontendInfo(self): return Frontend()
        class Nav:
            def __init__(self): self.calls = []
            def getCurrentService(self): return None
            def getRecordings(self, *args):
                self.calls.append(args)
                return [RecordService()] if len(args) == 2 else []
        nav = Nav()
        nim = types.ModuleType('Components.NimManager')
        nim.nimmanager = types.SimpleNamespace(nim_slots=[
            types.SimpleNamespace(slot=3, name='Tuner Three', getSlotType=lambda: 'DVB-S')])
        with patch.dict(sys.modules, {'enigma': enigma, 'Components': types.ModuleType('Components'),
                                      'Components.NimManager': nim}):
            rows = M.tuner_info(types.SimpleNamespace(nav=nav))
        self.assertEqual(nav.calls, [(False, 17)])
        self.assertEqual(rows[1], ('Laufende Aufnahmen', '1'))
        self.assertIn('· Aktiv', rows[2][1])

    def test_native_real_recording_filter_after_wrapper_signature_mismatch(self):
        enigma = types.ModuleType('enigma')
        enigma.pNavigation = types.SimpleNamespace(isRealRecording=23)
        class NativeNav:
            def __init__(self): self.calls = []
            def getRecordings(self, *args):
                self.calls.append(args)
                return [object(), object()]
        class Nav:
            def __init__(self):
                self.pnav = NativeNav()
                self.calls = []
            def getRecordings(self, simulate=False):
                self.calls.append((simulate,))
                return []
        nav = Nav()
        with patch.dict(sys.modules, {'enigma': enigma}):
            items, count, source = M._recordings(nav)
        self.assertEqual(nav.calls, [])
        self.assertEqual(nav.pnav.calls, [(False, 23)])
        self.assertEqual((len(items), count, source), (2, 2, 'real'))

    def test_timer_fallback_counts_running_record_entries_not_zaps(self):
        class Entry:
            def __init__(self, running, justplay):
                self.running, self.justplay = running, justplay
            def isRunning(self): return self.running
        nav = types.SimpleNamespace(
            getRecordings=lambda simulate=False: [],
            RecordTimer=types.SimpleNamespace(timer_list=[Entry(True, False), Entry(True, True), Entry(False, False)]))
        items, count, source = M._recordings(nav)
        self.assertEqual((items, count, source), ([], 1, 'timer'))

    def test_timer_fallback_unknown_when_running_api_is_missing(self):
        nav = types.SimpleNamespace(
            getRecordings=lambda simulate=False: [],
            RecordTimer=types.SimpleNamespace(timer_list=[types.SimpleNamespace(justplay=False)]))
        self.assertEqual(M._recordings(nav), ([], None, None))

    def test_timer_fallback_is_labeled_in_tuner_rows(self):
        nim = types.ModuleType('Components.NimManager')
        nim.nimmanager = types.SimpleNamespace(nim_slots=[])
        class Entry:
            justplay = False
            def isRunning(self): return True
        nav = types.SimpleNamespace(getCurrentService=lambda: None, getRecordings=lambda simulate=False: [],
                                    RecordTimer=types.SimpleNamespace(timer_list=[Entry()]))
        with patch.dict(sys.modules, {'Components': types.ModuleType('Components'), 'Components.NimManager': nim}):
            rows = M.tuner_info(types.SimpleNamespace(nav=nav))
        self.assertIn(('Aufnahmen (Timer)', '1'), rows)


if __name__ == '__main__':
    unittest.main()
