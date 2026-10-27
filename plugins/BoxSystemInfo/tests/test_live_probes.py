"""Tests for live read-only network and tuner metric probes."""
import importlib.util
from pathlib import Path
import types
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/probes.py'
spec = importlib.util.spec_from_file_location('probes_live', str(SOURCE))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class NetworkRateTests(unittest.TestCase):
    def test_first_sample_unknown_then_rates(self):
        ticks = iter([10, 11])
        sampler = M.NetworkRates(clock=lambda: next(ticks))
        self.assertEqual(sampler.sample('eth0', 1000, 2000, 10), (M.UNAVAILABLE, M.UNAVAILABLE))
        self.assertEqual(sampler.sample('eth0', 126000, 252000, 11), ('1.00 Mbit/s', '2.00 Mbit/s'))

    def test_counter_reset_and_bad_time_are_unknown_and_rebase(self):
        ticks = iter([10, 11])
        sampler = M.NetworkRates(clock=lambda: next(ticks))
        sampler.sample('eth0', 100, 100, 5)
        self.assertEqual(sampler.sample('eth0', 10, 200, 6), (M.UNAVAILABLE, '0.00 Mbit/s'))
        self.assertEqual(sampler.sample('eth0', 20, 300, 6), (M.UNAVAILABLE, M.UNAVAILABLE))
        self.assertEqual(sampler.sample('eth0', 30, 400, 7), ('0.00 Mbit/s', '0.00 Mbit/s'))

    def test_network_rows_read_sysfs_counters(self):
        def read(path):
            return {'/sys/class/net/eth0/carrier': '1', '/sys/class/net/eth0/speed': '100',
                    '/sys/class/net/eth0/statistics/rx_bytes': '100',
                    '/sys/class/net/eth0/statistics/tx_bytes': '200'}.get(path, '')
        ticks = iter([10, 11])
        sampler = M.NetworkRates(clock=lambda: next(ticks))
        with patch.object(M, '_read', side_effect=read), patch.object(M.os, 'listdir', return_value=['eth0']), \
                patch.object(M.os.path, 'exists', return_value=False):
            M.network_info(sampler)
            with patch.object(M, '_read', side_effect=lambda p: {'/sys/class/net/eth0/carrier': '1',
                  '/sys/class/net/eth0/speed': '100', '/sys/class/net/eth0/statistics/rx_bytes': '125100',
                  '/sys/class/net/eth0/statistics/tx_bytes': '250100'}.get(p, '')):
                rows = M.network_info(sampler)
        self.assertIn(('eth0 – Empfangen', '1.00 Mbit/s'), rows)
        self.assertIn(('eth0 – Gesendet', '2.00 Mbit/s'), rows)


class ActiveTunerTests(unittest.TestCase):
    def test_reads_live_frontend_status_without_other_tuner_apis(self):
        class Frontend:
            def getFrontendStatus(self):
                return {'tuner_signal_quality_db': 825, 'agc': 32768, 'ber': 0, 'tuner_locked': 1}
        service = types.SimpleNamespace(frontendInfo=lambda: Frontend())
        session = types.SimpleNamespace(nav=types.SimpleNamespace(getCurrentService=lambda: service))
        self.assertEqual(M.active_tuner_info(session), [('Signalqualität', '8.25 dB'),
                                                        ('AGC', '50%'), ('BER', '0'), ('Tuner-Lock', 'Ja')])

    def test_negative_driver_values_are_unavailable(self):
        class Frontend:
            def getFrontendStatus(self):
                return {'snr_db': -1, 'agc': -1, 'ber': -1, 'lock': -1}
        session = types.SimpleNamespace(nav=types.SimpleNamespace(
            getCurrentService=lambda: types.SimpleNamespace(frontendInfo=lambda: Frontend())))
        rows = dict(M.active_tuner_info(session))
        self.assertEqual(rows['Signalqualität'], M.UNAVAILABLE)
        self.assertEqual(rows['AGC'], M.UNAVAILABLE)
        self.assertEqual(rows['BER'], M.UNAVAILABLE)
        self.assertEqual(rows['Tuner-Lock'], M.UNAVAILABLE)

    def test_openpli_frontend_status_keys_use_documented_scaling(self):
        class Frontend:
            def getFrontendStatus(self):
                return {'tuner_signal_quality': 32768, 'tuner_signal_quality_db': 825,
                        'tuner_signal_power': 65535, 'tuner_bit_error_rate': 24,
                        'tuner_locked': 1}
        session = types.SimpleNamespace(nav=types.SimpleNamespace(getCurrentService=lambda:
            types.SimpleNamespace(frontendInfo=lambda: Frontend())))
        self.assertEqual(M.active_tuner_info(session), [('Signalqualität', '8.25 dB'),
            ('AGC', '100%'), ('BER', '24'), ('Tuner-Lock', 'Ja')])

    def test_openpli_quality_falls_back_to_driver_relative_percent(self):
        class Frontend:
            def getFrontendStatus(self):
                return {'tuner_signal_quality': 32768, 'tuner_signal_quality_db': None,
                        'tuner_signal_power': 16384, 'tuner_bit_error_rate': 0, 'tuner_locked': 0}
        session = types.SimpleNamespace(nav=types.SimpleNamespace(getCurrentService=lambda:
            types.SimpleNamespace(frontendInfo=lambda: Frontend())))
        self.assertEqual(M.active_tuner_info(session), [('Signalqualität', '50%'),
            ('AGC', '25%'), ('BER', '0'), ('Tuner-Lock', 'Nein')])

    def test_missing_live_dvb_is_unavailable(self):
        session = types.SimpleNamespace(nav=types.SimpleNamespace(getCurrentService=lambda: None))
        self.assertTrue(all(value == M.UNAVAILABLE for _, value in M.active_tuner_info(session)))


if __name__ == '__main__':
    unittest.main()
