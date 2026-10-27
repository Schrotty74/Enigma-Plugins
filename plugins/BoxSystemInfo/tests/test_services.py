"""Tests for privacy-safe reports and metadata-only release checks."""
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/services.py'
spec = importlib.util.spec_from_file_location('boxsysteminfo_services', str(SOURCE))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def snapshot():
    return {
        'cpu': {'cores': 4, 'load_1': 0.1, 'load_5': 0.2, 'load_15': 0.3},
        'memory': {'total_bytes': 1024, 'available_bytes': 512},
        'root_storage': {'total_bytes': 4096, 'free_bytes': 2048},
        'temperatures': {'soc_c': 48.5, 'drive_c': None},
    }


def release(version, draft=False, prerelease=False, asset_version=None):
    asset_version = asset_version or version
    return {'tag_name': 'boxsysteminfo-v' + version, 'draft': draft, 'prerelease': prerelease,
            'assets': [{'name': 'enigma2-plugin-extensions-boxsysteminfo_%s_armv7ahf-neon.ipk' % asset_version}]}


class DiagnosticTests(unittest.TestCase):
    def test_allowlisted_report_contains_only_numeric_metrics(self):
        result = M.diagnostic_report(snapshot())
        self.assertEqual(result['schema_version'], 1)
        self.assertEqual(result['metrics']['cpu']['cores'], 4)
        self.assertNotIn('hostname', json.dumps(result))

    def test_validated_plugin_version_and_optional_recording_storage(self):
        data = snapshot()
        data['recording_storage'] = {'total_bytes': 9000, 'free_bytes': 3000}
        result = M.diagnostic_report(data, plugin_version='0.1.11')
        self.assertEqual(result['plugin_version'], '0.1.11')
        self.assertEqual(result['metrics']['recording_storage']['free_bytes'], 3000)
        for invalid in ('private-version', '0.1/11', '../0.1.11'):
            with self.assertRaises(ValueError):
                M.diagnostic_report(snapshot(), plugin_version=invalid)

    def test_recording_storage_rejects_unknown_or_non_numeric_values(self):
        data = snapshot()
        data['recording_storage'] = {'total_bytes': 9000, 'free_bytes': 3000, 'mount': '/secret'}
        with self.assertRaises(ValueError):
            M.diagnostic_report(data)
        data['recording_storage'] = {'total_bytes': 9000, 'free_bytes': '/secret'}
        with self.assertRaises(ValueError):
            M.diagnostic_report(data)

    def test_rejects_unknown_keys_at_each_level_and_private_strings(self):
        candidates = []
        candidate = snapshot()
        candidate['hostname'] = 'receiver-secret'
        candidates.append(candidate)
        candidate = snapshot()
        candidate['cpu']['model'] = 'private model'
        candidates.append(candidate)
        candidate = snapshot()
        candidate['root_storage']['mount'] = '/private-example/device'
        candidates.append(candidate)
        for candidate in candidates:
            with self.assertRaises(ValueError):
                M.diagnostic_report(candidate)

    def test_rejects_missing_sections_nonfinite_and_bool_metrics(self):
        bad = snapshot()
        del bad['memory']
        with self.assertRaises(ValueError):
            M.diagnostic_report(bad)
        bad = snapshot()
        bad['cpu']['load_1'] = float('nan')
        with self.assertRaises(ValueError):
            M.diagnostic_report(bad)
        bad = snapshot()
        bad['cpu']['cores'] = True
        with self.assertRaises(ValueError):
            M.diagnostic_report(bad)

    def test_exports_unique_private_json_with_no_supplied_private_text(self):
        with tempfile.TemporaryDirectory() as directory:
            first = M.export_report(snapshot(), directory)
            second = M.export_report(snapshot(), directory)
            self.assertNotEqual(first, second)
            self.assertTrue(os.path.basename(first).startswith('boxsysteminfo-diagnostic-'))
            self.assertTrue(first.endswith('.json'))
            self.assertEqual(stat.S_IMODE(os.stat(first).st_mode), 0o600)
            with open(first) as handle:
                content = handle.read()
            self.assertNotIn('receiver-secret', content)
            self.assertNotIn('192.168.', content)
            self.assertEqual(json.loads(content), M.diagnostic_report(snapshot()))

    def test_invalid_report_creates_no_file(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = snapshot()
            bad['hostname'] = 'private'
            with self.assertRaises(ValueError):
                M.export_report(bad, directory)
            self.assertEqual(os.listdir(directory), [])

    def test_write_failure_removes_partial_export(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(M.json, 'dump', side_effect=OSError('write failed')):
                with self.assertRaises(OSError):
                    M.export_report(snapshot(), directory)
            self.assertEqual(os.listdir(directory), [])


class UpdateTests(unittest.TestCase):
    def mocked_response(self, payload):
        class Response:
            def read(self, size):
                self.read_size = size
                return json.dumps(payload).encode('utf-8')
            def close(self):
                pass
        return Response()

    def test_finds_numeric_newer_release_and_uses_fixed_url(self):
        payload = [release('0.1.11'), release('0.1.10'), release('0.1.12-beta'),
                   {'tag_name': 'boxsysteminfo-v0.2.0', 'draft': False, 'prerelease': False, 'assets': []}]
        with patch('urllib.request.urlopen', return_value=self.mocked_response(payload)) as open_url:
            result = M.check_update('0.1.9')
        self.assertEqual(result['status'], 'newer')
        self.assertEqual(result['version'], '0.1.11')
        self.assertEqual(result['release_url'], 'https://github.com/Schrotty74/Enigma-Plugins/releases/tag/boxsysteminfo-v0.1.11')
        self.assertEqual(open_url.call_args.kwargs['timeout'], M.TIMEOUT_SECONDS)

    def test_filters_drafts_prereleases_bad_tags_and_mismatched_assets(self):
        payload = [release('9.0', draft=True), release('8.0', prerelease=True),
                   release('7.0', asset_version='6.0'), release('3.0')]
        with patch('urllib.request.urlopen', return_value=self.mocked_response(payload)):
            self.assertEqual(M.check_update('3.0.0')['status'], 'current')

    def test_version_comparison_is_numeric_and_padding_aware(self):
        payload = [release('0.1.9'), release('0.1.10')]
        with patch('urllib.request.urlopen', return_value=self.mocked_response(payload)):
            self.assertEqual(M.check_update('0.1.9')['version'], '0.1.10')
        self.assertEqual(M.check_update('bad/version')['status'], 'error')

    def test_network_timeout_and_oversized_response_return_error(self):
        with patch('urllib.request.urlopen', side_effect=TimeoutError()):
            self.assertEqual(M.check_update('0.1.9')['status'], 'error')
        class HugeResponse:
            def read(self, size):
                return b'x' * size
            def close(self):
                pass
        with patch('urllib.request.urlopen', return_value=HugeResponse()):
            self.assertEqual(M.check_update('0.1.9')['status'], 'error')

    def test_cli_outputs_bounded_json(self):
        with patch.object(M, 'check_update', return_value={'status': 'current', 'version': '1.2', 'release_url': None}), \
                patch('builtins.print') as output:
            M._main(['services.py', 'updates', '1.2'])
        self.assertEqual(json.loads(output.call_args.args[0])['status'], 'current')
