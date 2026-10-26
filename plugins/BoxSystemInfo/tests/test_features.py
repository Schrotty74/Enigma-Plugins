"""Regression tests for recording storage, SMART details and detail-screen lifecycle."""
import ast
import importlib.util
import io
from pathlib import Path
import types
import sys
import unittest
from unittest.mock import patch
from test_plugin import M, TREE, Timer, Container

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('storage_worker', str(ROOT / 'src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/storage.py'))
S = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(S)


class StorageTests(unittest.TestCase):
    def test_unmounted_recording_directory_does_not_report_root_space(self):
        with patch('builtins.open', return_value=io.StringIO('/dev/root / ext4 rw 0 0\n')), patch.object(S.os.path, 'realpath', side_effect=lambda p: p), patch.object(S.os, 'statvfs') as stat:
            result = S.storage_info('/recordings/movie')
        self.assertNotIn('free', result)
        self.assertIn('Kein eigener', result['status'])
        stat.assert_not_called()

    def test_longest_mount_and_escaped_spaces_read_only(self):
        mounts = '/dev/root / ext4 rw 0 0\n/dev/sda1 /recordings ext4 rw 0 0\n/dev/sdb1 /recordings/my\\040disk ext4 ro 0 0\n'
        stats = types.SimpleNamespace(f_blocks=100, f_frsize=1024, f_bfree=20, f_bavail=10)
        with patch('builtins.open', return_value=io.StringIO(mounts)), patch.object(S.os.path, 'realpath', side_effect=lambda p: p), patch.object(S.os.path, 'isdir', return_value=True), patch.object(S.os, 'statvfs', return_value=stats):
            result = S.storage_info('/recordings/my disk/movie')
        self.assertEqual(result['mount'], '/recordings/my disk')
        self.assertEqual(result['device'], '/dev/sdb1')
        self.assertEqual(result['used'], 80 * 1024)
        self.assertEqual(result['free'], 10 * 1024)
        self.assertEqual(result['percent'], 88)
        self.assertTrue(result['read_only'])

    def test_network_source_not_exposed_in_result(self):
        mounts = 'example.invalid:/archive /recordings nfs rw 0 0\n'
        stats = types.SimpleNamespace(f_blocks=100, f_frsize=1024, f_bfree=20, f_bavail=20)
        with patch('builtins.open', return_value=io.StringIO(mounts)), patch.object(S.os.path, 'realpath', side_effect=lambda p: p), patch.object(S.os.path, 'isdir', return_value=True), patch.object(S.os, 'statvfs', return_value=stats):
            result = S.storage_info('/recordings/movie')
        self.assertEqual(result['device'], 'Netzwerk / virtuell')
        self.assertNotIn('example.invalid', str(result))

    def test_mount_prefix_is_not_a_path_boundary(self):
        mounts = '/dev/root / ext4 rw 0 0\n/dev/sda1 /record ext4 rw 0 0\n'
        with patch('builtins.open', return_value=io.StringIO(mounts)), patch.object(S.os.path, 'realpath', side_effect=lambda p: p):
            self.assertNotIn('free', S.storage_info('/record-other/movie'))


class RecordingPathTests(unittest.TestCase):
    def test_unset_path_uses_unique_enigma_mount_without_fixed_disk_path(self):
        module = types.ModuleType('Components.Harddisk')
        module.harddiskmanager = types.SimpleNamespace(getMountedPartitions=lambda: [types.SimpleNamespace(mountpoint='/'), types.SimpleNamespace(mountpoint='/recordings')])
        config = types.SimpleNamespace(usage=types.SimpleNamespace(default_path=types.SimpleNamespace(value='<default>')))
        with patch.object(M, 'config', config, create=True), patch.dict(sys.modules, {'Components.Harddisk': module}):
            self.assertEqual(M._recording_path(), '/recordings')

    def test_multiple_unconfigured_mounts_are_not_guessed(self):
        module = types.ModuleType('Components.Harddisk')
        module.harddiskmanager = types.SimpleNamespace(getMountedPartitions=lambda: [types.SimpleNamespace(mountpoint='/recordings'), types.SimpleNamespace(mountpoint='/other')])
        config = types.SimpleNamespace(usage=types.SimpleNamespace(default_path=types.SimpleNamespace(value='<default>')))
        with patch.object(M, 'config', config, create=True), patch.dict(sys.modules, {'Components.Harddisk': module}):
            self.assertEqual(M._recording_path(), '')


class SmartDetailTests(unittest.TestCase):
    def test_whitelisted_fields_only_and_raw_hours(self):
        output = ('Device Model: Example SSD\nSerial Number: REDACTED-EXAMPLE\n'
                  'SMART overall-health self-assessment test result: PASSED\n'
                  'ID# ATTRIBUTE_NAME FLAG VALUE WORST THRESH TYPE UPDATED WHEN_FAILED RAW_VALUE\n'
                  '9 Power_On_Hours 0x0032 100 100 --- Old_age Always - 123\n')
        self.assertEqual(M._parse_smart_details(output), {'model': 'Example SSD', 'health': 'Bestanden', 'hours': '123 Std.'})

    def test_failed_health_and_nvme_hours(self):
        self.assertTrue(M._parse_smart_details('SMART Health Status: FAILED!')['health_failed'])
        self.assertEqual(M._parse_smart_details('Power On Hours: 1,234')['hours'], '1234 Std.')
        self.assertTrue(M._parse_smart_details('', 8)['health_failed'])
        self.assertEqual(M._parse_smart_details('', -9), {})

    def test_warning_boundary_and_missing_data(self):
        self.assertFalse(M._temperature_warning('Nicht verfügbar', 60))
        self.assertFalse(M._temperature_warning('59.9°C', 60))
        self.assertTrue(M._temperature_warning('60.0°C (sda, SMART)', 60))


class AsyncFeatureTests(unittest.TestCase):
    def setUp(self):
        Container.instances = []
        Container.fail = False
        patches = [patch.object(M, 'eTimer', Timer, create=True), patch.object(M, 'eConsoleAppContainer', Container, create=True),
                   patch.object(M, '_find_executable', return_value='/usr/bin/python3'), patch.object(M, '_drive_hwmon', return_value=None)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def test_storage_query_completion_and_timeout_without_app_closed(self):
        values = []
        q = M.StorageQuery(values.append)
        q.start('/recordings/movie')
        self.assertEqual(values, [])
        Container.instances[-1].emit(b'{"free":1024,"status":"Verfuegbar"}', 0)
        self.assertEqual(values[0]['free'], 1024)
        q = M.StorageQuery(values.append)
        q.start('/recordings/movie')
        c = Container.instances[-1]
        q._timeout()
        self.assertTrue(c.killed)
        self.assertIn('Zeitlimit', values[-1]['status'])
        c.emit(b'{}', 0)
        self.assertEqual(len(values), 2)

    def test_storage_cancel_discards_late_result(self):
        values = []
        q = M.StorageQuery(values.append)
        q.start('/recordings/movie')
        c = Container.instances[-1]
        q.cancel()
        c.emit(b'{"free":1024}', 0)
        self.assertEqual(values, [])
        self.assertTrue(c.killed)

    def test_unknown_recording_path_does_not_start_process(self):
        values = []
        M.StorageQuery(values.append).start('')
        self.assertEqual(Container.instances, [])
        self.assertIn('Aufnahmepfad', values[0]['status'])

    def test_temperature_scan_continues_past_model_only_device(self):
        with patch.object(M, '_drive_devices', return_value=['/sys/block/sda', '/sys/block/sdb']):
            values = []
            q = M.DriveTemperatureQuery(values.append)
            q.start()
            Container.instances[-1].emit('Device Model: Example One', 0)
            self.assertEqual(values, [])
            Container.instances[-1].emit('Device Model: Example Two\nTemperature: 31 Celsius', 0)
        self.assertEqual(values, ['31.0°C (sdb, SMART)'])
        self.assertEqual(q.details['model'], 'Example Two')

    def test_preferred_recording_device_is_not_replaced_by_another_temperature(self):
        with patch.object(M, '_drive_devices', return_value=['/sys/block/sda', '/sys/block/sdb']):
            values = []
            q = M.DriveTemperatureQuery(values.append, '/dev/sdb1')
            q.start()
            self.assertEqual(Container.instances[-1].args[-1], '/dev/sdb')
            Container.instances[-1].emit('Device Model: Recording SSD', 0)
        self.assertEqual(len(Container.instances), 1)
        self.assertEqual(q.details['device'], '/dev/sdb')
        self.assertNotIn('SMART)', values[0])


class ScreenLifecycleTests(unittest.TestCase):
    def test_refresh_cancels_old_work_and_late_data_does_not_update_closed_screen(self):
        class Screen(dict):
            def __init__(self, session):
                dict.__init__(self)
                self.session, self.instance = session, None
                self.onClose, self.onLayoutFinish = [], []
            def close(self):
                for fn in self.onClose: fn()
        class Label:
            def __init__(self, text): self.text, self.instance = text, None
            def setText(self, text): self.text = text
        namespace = M.__dict__.copy()
        namespace.update(Screen=Screen, Label=Label, ActionMap=lambda *args: args[1],
                         config=types.SimpleNamespace(plugins=types.SimpleNamespace(boxsysteminfo=types.SimpleNamespace(theme=types.SimpleNamespace(value='midnight')))),
                         cpu_info=lambda: [('Kerne', '2')], network_info=lambda: [('LAN', 'Verbunden')], tuner_info=lambda session: [('Tuner-Frontends', '8')],
                         _recording_path=lambda: '/recordings/movie', _image_info=lambda: ('Example', '1', ''),
                         _box_model=lambda: 'Example Receiver', _cpu_name=lambda: 'ARM', _memory_info=lambda: ('1 MB / 4 MB', '25% belegt'),
                         _soc_temperature=lambda: '50.0°C', _root_usage=lambda: {'free': 1024, 'total': 4096, 'percent': 75},
                         _enigma_version=lambda: '1', _uptime=lambda: '1 Std.', _image_build_date=lambda: '—',
                         platform=types.SimpleNamespace(machine=lambda: 'armv7l', release=lambda: 'kernel', python_version=lambda: '3'),
                         gRGB=None, eTimer=Timer, eConsoleAppContainer=Container, _find_executable=lambda name: '/usr/bin/python3',
                         _drive_devices=lambda: ['/sys/block/sda'], _drive_hwmon=lambda devices: None)
        assignments = [n for n in TREE.body if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('VERSION','THEMES','SOC_WARNING','DRIVE_WARNING','STORAGE_WARNING') for t in n.targets)]
        classes = [n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name in ('DriveTemperatureQuery','StorageQuery','BoxSystemInfo','SystemDetails')]
        exec(compile(ast.Module(body=assignments+classes,type_ignores=[]),'screen','exec'), namespace)
        Container.instances = []
        screen = namespace['BoxSystemInfo'](types.SimpleNamespace())
        first = Container.instances[-1]
        screen.refresh()
        self.assertTrue(first.killed)
        first.emit('{"free":999}',0)
        Container.instances[-1].emit('{"path":"/recordings/movie","device":"/dev/sda1","percent":90}',0)
        smart = Container.instances[-1]
        smart.emit('Device Model: Example SSD\nTemperature: 34 Celsius',0)
        self.assertIn('34.0',screen['temperature_detail'].text)
        self.assertEqual(len(screen.detail_pages()),4)
        screen.refresh()
        last = Container.instances[-1]
        screen.close()
        last.emit('{}',0)
        self.assertTrue(last.killed)


if __name__ == '__main__': unittest.main()
