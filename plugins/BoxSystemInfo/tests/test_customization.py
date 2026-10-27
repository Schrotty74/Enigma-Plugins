"""Exercise saved card choices, warning settings and diagnostic UI integration."""
import ast
import types
import unittest
from unittest.mock import patch
from test_plugin import M, TREE, Timer, Container


class Element:
    def __init__(self, value):
        self.value, self.saved = value, 0
    def save(self):
        self.saved += 1


class Label:
    def setText(self, text):
        self.text = text


def screen_fixture():
    class Screen(dict):
        pass
    options = types.SimpleNamespace(**{key: Element(value) for key, value in {
        'card1': 'temperature', 'card2': 'memory', 'card3': 'root',
        'soc_warning': '80', 'drive_warning': '60', 'storage_warning': '90',
        'memory_warning': '90', 'theme': 'midnight',
    }.items()})
    namespace = M.__dict__.copy()
    namespace.update(Screen=Screen, config=types.SimpleNamespace(plugins=types.SimpleNamespace(boxsysteminfo=options)),
                     configfile=types.SimpleNamespace(save=lambda: None))
    nodes = [n for n in TREE.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id in ('VERSION', 'THEMES', 'SOC_WARNING', 'DRIVE_WARNING', 'STORAGE_WARNING')
        for t in n.targets)]
    nodes += [n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name in ('_setting_value', '_threshold')]
    nodes += [n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'BoxSystemInfo']
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'customization', 'exec'), namespace)
    box = dict.__new__(namespace['BoxSystemInfo'])
    dict.__init__(box)
    for position in ('temperature', 'memory', 'storage'):
        for suffix in ('title', 'value', 'detail'):
            box[position + '_' + suffix] = Label()
    box._is_closed = False
    box._memory = {'total': 1000, 'used': 700, 'available': 300}
    box._root = {'free': 100, 'total': 1000, 'percent': 90}
    box._recording = {'free': 500, 'total': 2000, 'percent': 75, 'path': 'PRIVATE_RECORDING_PATH'}
    box._soc_value, box._drive_value = '79.0°C', '59.0°C'
    box._drive_details = {}
    box._network_current = ('eth0', 2.0, 1.0)
    box._card_data = {}
    box.apply_theme = lambda: None
    box._notify_details = lambda: None
    return box, options, namespace


class CustomizationTests(unittest.TestCase):
    def test_default_cards_and_replacing_root_with_recordings(self):
        box, options, namespace = screen_fixture()
        box._render_cards()
        self.assertEqual(box['temperature_title'].text, 'Temperaturen')
        self.assertEqual(box['memory_value'].text, '70% belegt')
        self.assertEqual(box['storage_title'].text, 'Root-Speicher')
        box._editing_card = 'card3'
        box._card_selected(('Aufnahmespeicher', 'recording'))
        self.assertEqual(box['storage_title'].text, 'Aufnahmespeicher')
        self.assertEqual(options.card3.saved, 1)
        self.assertNotIn('PRIVATE', box['storage_detail'].text)

    def test_duplicate_card_selection_swaps_the_existing_slot(self):
        box, options, namespace = screen_fixture()
        box._editing_card = 'card3'
        box._card_selected(('Arbeitsspeicher', 'memory'))
        self.assertEqual((options.card1.value, options.card2.value, options.card3.value),
                         ('temperature', 'root', 'memory'))

    def test_warning_settings_change_only_display_flags_at_boundaries(self):
        box, options, namespace = screen_fixture()
        box._render_cards()
        self.assertFalse(box._card_data['temperature'][3])
        self.assertFalse(box._card_data['temperature'][4])
        self.assertTrue(box._card_data['root'][3])
        box._editing_threshold = 'drive_warning'
        box._threshold_value_selected(('55 °C', '55'))
        self.assertTrue(box._card_data['temperature'][4])
        self.assertEqual(options.drive_warning.saved, 1)

    def test_diagnostic_action_passes_only_explicit_metrics(self):
        box, options, namespace = screen_fixture()
        exports = []
        namespace['_read'] = lambda *args: '0.12 0.34 0.56 1/10 1'
        namespace['export_report'] = lambda snapshot, plugin_version: exports.append((snapshot, plugin_version)) or 'diagnostic.json'
        namespace['MessageBox'] = types.SimpleNamespace(TYPE_INFO=0)
        box.session = types.SimpleNamespace(open=lambda *args, **kwargs: None)
        box._cpu_rows = [('Kerne', '2')]
        box.export_diagnostics()
        self.assertEqual(exports[0][0]['cpu']['cores'], 2)
        self.assertEqual(exports[0][0]['cpu']['load_15'], 0.56)
        self.assertNotIn('PRIVATE', repr(exports))
        self.assertEqual(exports[0][1], '0.1.11')


class UpdateWorkerTests(unittest.TestCase):
    def make_query(self, values):
        namespace = M.__dict__.copy()
        namespace.update(eConsoleAppContainer=Container, VERSION='0.1.11',
                         _find_executable=lambda name: '/usr/bin/python3')
        node = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'UpdateQuery')
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'update_worker', 'exec'), namespace)
        with patch.object(M, 'eTimer', Timer, create=True):
            return namespace['UpdateQuery'](values.append)

    def test_timeout_kills_worker_and_ignores_late_completion(self):
        values = []
        query = self.make_query(values)
        query.start()
        worker = query.container
        query._timeout()
        worker.emit('{"status":"newer","version":"9.0"}', 0)
        self.assertTrue(worker.killed)
        self.assertEqual(values, [{'status': 'error'}])

    def test_cancel_discards_pending_update_and_completion_reads_json(self):
        values = []
        query = self.make_query(values)
        query.start()
        worker = query.container
        query.cancel()
        worker.emit('{"status":"current"}', 0)
        self.assertEqual(values, [])
        query = self.make_query(values)
        query.start()
        query.container.emit('{"status":"current","version":"0.1.11"}', 0)
        self.assertEqual(values, [{'status': 'current', 'version': '0.1.11'}])


if __name__ == '__main__':
    unittest.main()
