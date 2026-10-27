"""Tests for byte-based memory metrics and in-memory history helpers."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          'src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/metrics.py')
SPEC = importlib.util.spec_from_file_location('metrics', str(SOURCE))
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class MemoryTests(unittest.TestCase):
    def test_meminfo_parses_bytes_and_separate_cache_fields(self):
        result = M.parse_memory('''MemTotal:       1000 kB
MemAvailable:    400 kB
MemFree:         100 kB
Buffers:          20 kB
Cached:          300 kB
SReclaimable:     50 kB
Shmem:            10 kB
SwapTotal:       200 kB
SwapFree:         75 kB
''')
        self.assertEqual(result, {'total': 1024000, 'available': 409600,
                                  'used': 614400, 'free': 102400,
                                  'cache': 348160, 'buffers': 20480,
                                  'swap_total': 204800, 'swap_free': 76800,
                                  'swap_used': 128000})

    def test_available_fallback_and_clamping(self):
        result = M.parse_memory('''MemTotal: 100 kB
MemFree: 80 kB
Buffers: 50 kB
Cached: 50 kB
SReclaimable: 20 kB
Shmem: 10 kB
SwapTotal: 10 kB
SwapFree: 99 kB
''')
        self.assertEqual(result['available'], result['total'])
        self.assertEqual(result['used'], 0)
        self.assertEqual(result['free'], 80 * 1024)
        self.assertEqual(result['swap_free'], result['swap_total'])
        self.assertEqual(result['swap_used'], 0)

    def test_bad_or_missing_fields_are_safe(self):
        self.assertEqual(M.parse_memory('MemTotal: invalid kB\n'),
                         {'total': 0, 'available': 0, 'used': 0, 'free': 0,
                          'cache': 0, 'buffers': 0, 'swap_total': 0,
                          'swap_free': 0, 'swap_used': 0})


class HistoryTests(unittest.TestCase):
    def test_rolling_window_capacity_unknown_gaps_and_immutable_copy(self):
        history = M.SessionHistory(window=10, maxpoints=3, clock=lambda: 0)
        history.append('ram', 1, now=1)
        history.append('ram', None, now=2)
        history.append('ram', float('nan'), now=3)
        history.append('ram', 4, now=4)
        points = history.points('ram', now=4)
        self.assertEqual(points, ((2.0, None), (3.0, None), (4.0, 4.0)))
        self.assertIsInstance(points, tuple)
        history.append('ram', 5, now=20)
        self.assertEqual(history.points('ram', now=20), ((20.0, 5.0),))

    def test_points_prune_when_no_samples_arrive_and_clear(self):
        history = M.SessionHistory(window=5, clock=lambda: 0)
        history.append('cpu', 10, now=1)
        self.assertEqual(history.points('cpu', now=7), ())
        history.append('cpu', 20, now=8)
        history.clear()
        self.assertEqual(history.points('cpu', now=8), ())

    def test_append_prunes_stale_other_streams_and_bounds_stream_count(self):
        history = M.SessionHistory(window=5, maxseries=2, clock=lambda: 0)
        history.append('stale', 1, now=0)
        history.append('active-a', 2, now=10)
        self.assertEqual(history.points('stale', now=10), ())
        history.append('active-b', 3, now=11)
        self.assertEqual(history.points('active-a', now=11), ((10.0, 2.0),))
        history.append('active-c', 4, now=12)
        self.assertEqual(history.points('active-a', now=12), ())
        self.assertEqual(history.points('active-b', now=12), ((11.0, 3.0),))
        self.assertEqual(history.points('active-c', now=12), ((12.0, 4.0),))


class GraphTests(unittest.TestCase):
    def test_time_positions_follow_actual_timestamps_and_gaps_split_segments(self):
        points = ((0, 1), (300, 2), (None, None), (450, 3), (600, 4))
        segments = M.graph_segments(points, 120, 60, minimum=0, maximum=4,
                                    now=600, window=600)
        self.assertEqual(segments, [[(0.0, 45.0), (60.0, 30.0)],
                                    [(90.0, 15.0), (120.0, 0.0)]])

    def test_constant_values_are_visible_and_all_coordinates_are_clipped(self):
        segments = M.graph_segments(((100, -20), (200, 5), (300, 99)),
                                    40, 20, minimum=5, maximum=5,
                                    now=300, window=200)
        self.assertEqual(segments, [[(0.0, 10.0), (20.0, 10.0), (40.0, 10.0)]])
        for segment in segments:
            for x, y in segment:
                self.assertGreaterEqual(x, 0)
                self.assertLessEqual(x, 40)
                self.assertGreaterEqual(y, 0)
                self.assertLessEqual(y, 20)

    def test_stale_and_nonfinite_points_do_not_draw(self):
        self.assertEqual(M.graph_segments(((0, 1), (float('nan'), 2)), 10, 10,
                                          now=1000, window=10), [])


if __name__ == '__main__':
    unittest.main()
