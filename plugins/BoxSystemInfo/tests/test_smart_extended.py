"""Allowlist tests for SMART wear and error parsing."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/smart.py'
spec = importlib.util.spec_from_file_location('smart_extended', str(SOURCE))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def ata(name, value, raw):
    return '  5 %-28s 0x0033   %3d   099   000    Old_age   Always       -       %s' % (name, value, raw)


class SmartExtendedTests(unittest.TestCase):
    def test_known_errors_and_explicit_remaining_life(self):
        result = M.parse_smart_wear('\n'.join([
            ata('Reallocated_Sector_Ct', 100, '2'),
            ata('Current_Pending_Sector', 100, '0'),
            ata('Percent_Lifetime_Remain', 94, 'not interpreted'),
        ]))
        self.assertEqual(result['wear_rows'], [('Remappte Sektoren', '2'),
                                               ('Ausstehende Sektoren', '0'),
                                               ('Verbleibende Lebensdauer', '94%')])
        self.assertEqual(result['wear_warning'], 'SMART-Fehler erkannt')

    def test_unknown_attributes_and_normalized_wear_count_do_not_create_life_estimate(self):
        result = M.parse_smart_wear('\n'.join([
            ata('Wear_Leveling_Count', 4, '4'),
            ata('Mystery_Vendor_Field', 1, 'SECRET_SERIAL_123'),
        ]))
        self.assertEqual(result, {'wear_rows': [], 'wear_warning': None})

    def test_nvme_percentage_used_and_media_errors(self):
        result = M.parse_smart_wear('Percentage Used: 135%\nMedia and Data Integrity Errors: 1\n')
        self.assertEqual(result['wear_rows'], [('Verschleiß (Percentage Used)', '135%'), ('Medienfehler', '1')])
        self.assertEqual(result['wear_warning'], 'Verschleißgrenze erreicht')

    def test_zero_error_counters_are_not_warned_and_invalid_percent_is_omitted(self):
        result = M.parse_smart_wear(ata('UDMA_CRC_Error_Count', 100, '0') + '\n' +
                                    ata('Percent_Lifetime_Remain', 101, '101'))
        self.assertEqual(result, {'wear_rows': [('Übertragungsfehler', '0')], 'wear_warning': None})

    def test_parser_does_not_return_serials_or_unrecognized_output(self):
        result = M.parse_smart_wear('Serial Number: PRIVATE123\nModel Family: Private Model\n')
        self.assertEqual(result, {'wear_rows': [], 'wear_warning': None})
        self.assertNotIn('PRIVATE123', repr(result))

    def test_smartctl_variant_without_when_failed_uses_column_eight_as_raw(self):
        line = '  5 Reallocated_Sector_Ct 0x0033 100 099 000 Old_age Always 3'
        result = M.parse_smart_wear(line)
        self.assertEqual(result, {'wear_rows': [('Remappte Sektoren', '3')],
                                  'wear_warning': 'SMART-Fehler erkannt'})

    def test_supported_extended_counters_and_reserved_space(self):
        result = M.parse_smart_wear('\n'.join([
            ata('Reported_Uncorrect', 100, '2'),
            ata('Host_Writes_GiB', 100, '448'),
            ata('Available_Reservd_Space', 100, '100'),
            ata('Media_Wearout_Indicator', 1, '0x000600000006'),
        ]))
        self.assertEqual(result['wear_rows'], [('Gemeldete unkorrigierbare Fehler', '2'),
            ('Host-Schreibmenge', '448 GiB'), ('Verfügbare Reservesektoren', '100%')])
        self.assertEqual(result['wear_warning'], 'SMART-Fehler erkannt')


if __name__ == '__main__':
    unittest.main()
