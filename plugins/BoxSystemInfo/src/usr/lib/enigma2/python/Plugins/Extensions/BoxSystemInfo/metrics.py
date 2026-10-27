"""Memory metrics and small, GUI-independent history graph helpers.

All memory values are bytes. History points are ``(monotonic_seconds, value)``
pairs; ``None`` values are retained as gaps. ``graph_segments`` maps them into
viewport pixel coordinates and returns one list of points per continuous line.
"""
from __future__ import print_function

import math
import time


_MEM_FIELDS = ("MemTotal", "MemAvailable", "MemFree", "Buffers", "Cached",
               "SReclaimable", "Shmem", "SwapTotal", "SwapFree")


def _finite(value):
    return not math.isnan(value) and not math.isinf(value)


def parse_memory(text):
    """Parse Linux /proc/meminfo and return byte totals suitable for display."""
    raw = {}
    for line in (text or "").splitlines():
        parts = line.split()
        if len(parts) < 2 or parts[0].rstrip(":") not in _MEM_FIELDS:
            continue
        try:
            amount = float(parts[1])
            if not _finite(amount) or amount < 0:
                continue
            # procfs reports these fields in kB; tolerate an omitted unit as kB.
            raw[parts[0].rstrip(":")] = int(amount * 1024) if len(parts) < 3 or parts[2].lower() == "kb" else int(amount)
        except (TypeError, ValueError, OverflowError):
            continue

    def bounded(name, maximum=None):
        value = raw.get(name, 0)
        return max(0, min(value, maximum)) if maximum is not None else max(0, value)

    total = bounded("MemTotal")
    memfree = bounded("MemFree", total)
    buffers = bounded("Buffers", total)
    cached = bounded("Cached", total)
    reclaimable = bounded("SReclaimable", total)
    shmem = bounded("Shmem", total)
    cache = max(0, min(total, cached + reclaimable - shmem))
    if "MemAvailable" in raw:
        available = bounded("MemAvailable", total)
    else:
        available = min(total, max(0, memfree + buffers + cached + reclaimable - shmem))
    swap_total = bounded("SwapTotal")
    swap_free = bounded("SwapFree", swap_total)
    return {
        "total": total,
        "available": available,
        "used": max(0, total - available),
        "free": memfree,
        "cache": cache,
        "buffers": buffers,
        "swap_total": swap_total,
        "swap_free": swap_free,
        "swap_used": max(0, swap_total - swap_free),
    }


class SessionHistory(object):
    """Bounded in-memory rolling history for live system metrics."""
    def __init__(self, window=600.0, maxpoints=300, clock=None, maxseries=16):
        self.window = max(0.0, float(window))
        self.maxpoints = max(1, int(maxpoints))
        self.maxseries = max(1, int(maxseries))
        self.clock = clock or getattr(time, "monotonic", time.time)
        self._series = {}

    def _now(self, now):
        value = self.clock() if now is None else now
        value = float(value)
        if not _finite(value):
            raise ValueError("timestamp must be finite")
        return value

    @staticmethod
    def _value(value):
        if value is None:
            return None
        try:
            numeric = float(value)
            return numeric if _finite(numeric) else None
        except (TypeError, ValueError, OverflowError):
            return None

    def _prune(self, key, now):
        series = self._series.get(key)
        if not series:
            return
        cutoff = now - self.window
        # Appends use a monotonic clock in normal use; handle out-of-order data
        # as well by retaining only samples inside the requested time window.
        series[:] = [(stamp, value) for stamp, value in series if stamp >= cutoff]
        if len(series) > self.maxpoints:
            del series[:-self.maxpoints]
        if not series:
            self._series.pop(key, None)

    def _prune_all(self, now):
        for key in list(self._series):
            self._prune(key, now)

    def append(self, key, value, now=None):
        """Append a finite numeric sample; invalid/unknown values become gaps."""
        stamp = self._now(now)
        self._prune_all(stamp)
        if key not in self._series and len(self._series) >= self.maxseries:
            oldest = min(self._series,
                         key=lambda series_key: max(item[0] for item in self._series[series_key]))
            del self._series[oldest]
        series = self._series.setdefault(key, [])
        series.append((stamp, self._value(value)))
        self._prune(key, stamp)

    def points(self, key, now=None):
        """Return an immutable tuple copy, pruning aged samples even when paused."""
        stamp = self._now(now)
        self._prune(key, stamp)
        return tuple(self._series.get(key, ()))

    def clear(self):
        """Discard all samples."""
        self._series.clear()


def graph_segments(points, width, height, minimum=None, maximum=None,
                   now=None, window=600.0):
    """Map timestamped points into clipped viewport segments.

    X uses each sample's actual timestamp in the trailing ``window``. Y is
    scaled to the supplied limits (or the finite visible sample range). Gaps
    and samples outside the time window split lines. Returned coordinates are
    floats and remain within ``[0,width]`` / ``[0,height]``.
    """
    try:
        width, height, window = float(width), float(height), float(window)
        if not all(_finite(v) for v in (width, height, window)) or width <= 0 or height <= 0 or window <= 0:
            return []
        parsed = []
        for point in points:
            try:
                stamp, value = point
                stamp = float(stamp)
                value = None if value is None else float(value)
                if not _finite(stamp):
                    stamp = None
                    value = None
                elif value is not None and not _finite(value):
                    value = None
                parsed.append((stamp, value))
            except (TypeError, ValueError, OverflowError):
                parsed.append((None, None))
        if now is None:
            stamps = [stamp for stamp, value in parsed if stamp is not None]
            now_value = max(stamps) if stamps else 0.0
        else:
            now_value = float(now)
        if not _finite(now_value):
            return []
        start = now_value - window
        visible = [(stamp, value) for stamp, value in parsed
                   if stamp is not None and start <= stamp <= now_value and value is not None]
        if minimum is None:
            values = [value for stamp, value in visible]
            minimum = min(values) if values else 0.0
        else:
            minimum = float(minimum)
        if maximum is None:
            values = [value for stamp, value in visible]
            maximum = max(values) if values else minimum
        else:
            maximum = float(maximum)
        if not _finite(minimum) or not _finite(maximum):
            return []
        if maximum < minimum:
            minimum, maximum = maximum, minimum
        if maximum == minimum:
            # Constant series is centered so it remains visible.
            ycoord = height / 2.0
        segments, current = [], []
        for stamp, value in parsed:
            if stamp is None or value is None or stamp < start or stamp > now_value:
                if current:
                    segments.append(current)
                    current = []
                continue
            x = max(0.0, min(width, (stamp - start) * width / window))
            if maximum == minimum:
                y = ycoord
            else:
                clipped = max(minimum, min(maximum, value))
                y = height - (clipped - minimum) * height / (maximum - minimum)
            current.append((x, max(0.0, min(height, y))))
        if current:
            segments.append(current)
        return segments
    except (TypeError, ValueError, OverflowError):
        return []
