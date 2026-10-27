"""Verify shipped catalogs, language selection and translation coverage."""
import ast
import gettext
import importlib.util
from pathlib import Path
import re
import sys
import types
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1] / 'src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo'
spec = importlib.util.spec_from_file_location('box_i18n', str(BASE / 'i18n.py'))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class TranslationTests(unittest.TestCase):
    def modules(self, selection, image='de_DE'):
        config = types.ModuleType('Components.config')
        config.config = types.SimpleNamespace(plugins=types.SimpleNamespace(
            boxsysteminfo=types.SimpleNamespace(language=types.SimpleNamespace(value=selection))))
        language = types.ModuleType('Components.Language')
        language.language = types.SimpleNamespace(getLanguage=lambda: image)
        return {'Components.config': config, 'Components.Language': language}

    def test_empty_label_never_displays_catalog_header(self):
        for lang in ('de', 'en'):
            with patch.dict(sys.modules, self.modules(lang)):
                self.assertEqual(M._(''), '')

    def test_image_language_and_english_fallback(self):
        for image, expected in [('de_DE', 'Speicherstatus'), ('en_GB', 'Storage status'), ('fr_FR', 'Storage status')]:
            with patch.dict(sys.modules, self.modules('system', image)):
                self.assertEqual(M._('Speicherstatus'), expected)

    def test_language_override_changes_without_restart(self):
        with patch.dict(sys.modules, self.modules('en')):
            self.assertEqual(M._('Nicht verfügbar'), 'Unavailable')
        with patch.dict(sys.modules, self.modules('de')):
            self.assertEqual(M._('Nicht verfügbar'), 'Nicht verfügbar')

    def test_english_catalog_covers_source_and_preserves_placeholders(self):
        catalog = gettext.translation('BoxSystemInfo', str(BASE / 'locale'), languages=['en'])
        for path in (BASE / 'plugin.py', BASE / 'probes.py', BASE / 'smart.py', BASE / 'charts.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == '_'
                        and node.args and isinstance(node.args[0], ast.Constant)):
                    continue
                source = node.args[0].value
                self.assertIn(source, catalog._catalog, (path.name, source))
                expected = re.findall(r'%(?:\.\d+)?[sdif%]', source)
                actual = re.findall(r'%(?:\.\d+)?[sdif%]', catalog.gettext(source))
                self.assertEqual(expected, actual, source)


if __name__ == '__main__':
    unittest.main()
