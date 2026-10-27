"""Focused regression tests; Enigma2 callbacks use test doubles on the host."""
import ast
import importlib.util
import json
import glob
import os
from pathlib import Path
import re
import sys
import time
import types
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/plugin.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))
# Load the actual helpers without requiring an Enigma2 installation on the host.
NODES = [n for n in TREE.body if isinstance(n, ast.FunctionDef) or
         isinstance(n, ast.ClassDef) and n.name in ('DriveTemperatureQuery', 'StorageQuery')]
M = types.ModuleType('plugin_helpers')
smart_spec = importlib.util.spec_from_file_location('smart_helpers', str(SOURCE.parent / 'smart.py'))
smart_helpers = importlib.util.module_from_spec(smart_spec)
smart_spec.loader.exec_module(smart_helpers)
metrics_spec = importlib.util.spec_from_file_location('metrics_helpers', str(SOURCE.parent / 'metrics.py'))
metrics_helpers = importlib.util.module_from_spec(metrics_spec)
metrics_spec.loader.exec_module(metrics_helpers)
M.__dict__.update(os=os, glob=glob, re=re, time=time, json=json, __file__=str(SOURCE),
                  _=lambda text: text, parse_smart_wear=smart_helpers.parse_smart_wear,
                  parse_memory=metrics_helpers.parse_memory, SessionHistory=metrics_helpers.SessionHistory)
exec(compile(ast.Module(body=NODES, type_ignores=[]), str(SOURCE), 'exec'), M.__dict__)

# Only the temperature table header/row from the observed device; no identifiers.
ATA = ('ID# ATTRIBUTE_NAME FLAG VALUE WORST THRESH TYPE UPDATED WHEN_FAILED RAW_VALUE\n'
       '194 Temperature_Celsius 0x0022 065 047 --- Old_age Always - 35 (Min/Max 18/47)\n')


class Timer:
    def __init__(self):
        self.callback = []
        self.running = False
    def start(self, milliseconds, once):
        self.running = True
    def stop(self):
        self.running = False


class Container:
    instances = []
    fail = False
    def __init__(self):
        self.dataAvail = []
        self.appClosed = []
        self.killed = False
        self.instances.append(self)
    def execute(self, *args):
        self.args = args
        return self.fail
    def kill(self):
        self.killed = True
    def emit(self, output, code):
        for cb in self.dataAvail[:]:
            cb(output)
        for cb in self.appClosed[:]:
            cb(code)


class ParserTests(unittest.TestCase):
    def test_observed_ata_raw_not_normalized_or_minmax(self):
        self.assertEqual(M._parse_smart_temperature(ATA), '35.0°C')
    def test_alternate_ata_table(self):
        self.assertEqual(M._parse_smart_temperature(
            'ID# ATTRIBUTE_NAME FLAGS VALUE WORST THRESH FAIL RAW_VALUE\n'
            '190 Airflow_Temperature_Cel -O---K 070 060 000 - 30\n'), '30.0°C')
    def test_nvme_scsi_and_kelvin(self):
        for output, expected in [('Temperature: 38 Celsius', '38.0°C'),
                                 ('Current Drive Temperature: 29 C', '29.0°C'),
                                 ('Temperature: 300 Kelvin', '26.9°C')]:
            self.assertEqual(M._parse_smart_temperature(output), expected)
    def test_missing_temperature(self):
        self.assertIsNone(M._parse_smart_temperature('Device is in STANDBY mode'))
        self.assertIsNone(M._parse_smart_temperature('194 Temperature_Celsius 065'))


class MetadataTests(unittest.TestCase):
    def test_observed_enigma_info(self):
        data = "displaydistro='OpenPLi'\nimageversion='scarthgap'\nimagebuild='c09e297d'\n"
        with patch.dict(sys.modules, {'Components.SystemInfo': None, 'boxbranding': None}), \
                patch.object(M, '_read', side_effect=lambda p, d='': data if p == '/usr/lib/enigma.info' else d):
            self.assertEqual(M._image_info(), ('OpenPLi', 'scarthgap', 'c09e297d'))
    def test_os_release_without_invented_build(self):
        with patch.dict(sys.modules, {'Components.SystemInfo': None, 'boxbranding': None}), \
                patch.object(M, '_read', side_effect=lambda p, d='': 'NAME="Example"\nVERSION_ID="7.5"' if p == '/etc/os-release' else d):
            self.assertEqual(M._image_info(), ('Example', '7.5', ''))
    def test_boxinfo_precedence(self):
        module = types.ModuleType('Components.SystemInfo')
        module.BoxInfo = types.SimpleNamespace(getItem=lambda k: {'displaydistro': 'OpenATV', 'imageversion': '7.6', 'imagebuild': '42'}.get(k))
        with patch.dict(sys.modules, {'Components.SystemInfo': module, 'boxbranding': None}), patch.object(M, '_read', return_value=''):
            self.assertEqual(M._image_info(), ('OpenATV', '7.6', '42'))
    def test_observed_compiledate(self):
        with patch.dict(sys.modules, {'Components.SystemInfo': None}), patch.object(M, '_read', return_value="compiledate='20261011'"):
            self.assertEqual(M._image_build_date(), '11.10.2026')
    def test_native_enigma_version(self):
        module = types.ModuleType('enigma')
        module.getEnigmaVersionString = lambda: '2026-10-10-scarthgap'
        with patch.dict(sys.modules, {'enigma': module}):
            self.assertEqual(M._enigma_version(), '2026-10-10-scarthgap')
    def test_bundled_tool_preferred(self):
        self.assertEqual(M._find_executable('smartctl'), str(SOURCE.parent / 'bin/smartctl'))
    def test_skin_geometry_and_headings(self):
        screen = ET.fromstring(M._systeminfo_skin())
        names = []
        for widget in screen.findall('widget'):
            names.append(widget.attrib['name'])
            x, y = map(int, widget.attrib['position'].split(','))
            w, h = map(int, widget.attrib['size'].split(','))
            self.assertTrue(0 <= x < x + w <= 1120 and 0 <= y < y + h <= 650)
            if widget.attrib['name'] in ('boxhead', 'imagehead'):
                self.assertEqual(widget.attrib['zPosition'], '1')
        self.assertEqual(len(names), len(set(names)))
    def test_executable_uses_path(self):
        with patch.dict(os.environ, {'PATH': '/opt/tools'}), \
                patch.object(os.path, 'isfile', side_effect=lambda p: p == '/opt/tools/smartctl'), patch.object(os, 'access', return_value=True):
            self.assertEqual(M._find_executable('smartctl'), '/opt/tools/smartctl')


class AsyncTests(unittest.TestCase):
    def setUp(self):
        Container.instances = []
        Container.fail = False
        self.patches = [patch.object(M, 'eTimer', Timer, create=True),
                        patch.object(M, 'eConsoleAppContainer', Container, create=True),
                        patch.object(M, '_find_executable', return_value='/usr/sbin/smartctl'),
                        patch.object(M, '_drive_devices', return_value=['/sys/block/sda']),
                        patch.object(M, '_drive_hwmon', return_value=None)]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        self.values = []
        self.query = M.DriveTemperatureQuery(self.values.append)
    def test_chunked_valid_output(self):
        self.query.start()
        self.assertEqual(self.values, [])
        c = Container.instances[-1]
        self.assertEqual(c.args, ('/usr/sbin/smartctl', '/usr/sbin/smartctl', '-n', 'standby,3', '-i', '-H', '-A', '/dev/sda'))
        c.dataAvail[0](ATA[:55].encode())
        c.emit(ATA[55:].encode(), 8)  # health warning does not invalidate temperature
        self.assertEqual(self.values, ['35.0°C (sda, SMART)'])
        self.assertEqual(c.appClosed, [])
        self.assertFalse(self.query.timer.running)
    def test_timeout_kills_and_reports(self):
        self.query.start()
        c = Container.instances[-1]
        self.query._timeout()
        self.assertTrue(c.killed)
        self.assertEqual(self.values, ['SMART-Zeitlimit erreicht'])
        c.emit('', -9)
        self.assertEqual(self.values, ['SMART-Zeitlimit erreicht'])
    def test_close_cancels_without_late_update(self):
        self.query.start()
        c = Container.instances[-1]
        self.query.cancel()
        c.emit(ATA, 0)
        self.assertTrue(c.killed)
        self.assertEqual(self.values, [])
    def test_standby_is_not_retried(self):
        self.query.start()
        Container.instances[-1].emit('Device is in STANDBY mode', 3)
        self.assertEqual(self.values, ['Laufwerk im Standby'])
        self.assertEqual(len(Container.instances), 1)
    def test_explicit_type_request_retries_sat(self):
        self.query.start()
        Container.instances[-1].emit('Unknown USB bridge. Please specify device type with the -d option.', 1)
        c = Container.instances[-1]
        self.assertIn('sat', c.args)
        c.emit(ATA, 0)
        self.assertEqual(self.values, ['35.0°C (sda, SMART)'])
    def test_launch_failure(self):
        Container.fail = True
        self.query.start()
        self.assertEqual(self.values, ['SMART-Abfrage fehlgeschlagen'])
    def test_missing_tool(self):
        with patch.object(M, '_find_executable', return_value=None):
            self.query.start()
        self.assertEqual(self.values, ['smartctl fehlt'])
        self.assertEqual(Container.instances, [])


if __name__ == '__main__':
    unittest.main()
