# -*- coding: utf-8 -*-
"""Read-only CPU, network and Enigma2 tuner information probes."""
from __future__ import print_function

import os
import re
import time

try:
    from .i18n import _
except (ImportError, ValueError):
    def _(text):
        return text

UNAVAILABLE = "Nicht verfügbar"


def _read(path):
    try:
        with open(path, "r") as handle:
            return handle.read().strip()
    except (IOError, OSError):
        return ""


def _cpu_ids(text):
    result = set()
    try:
        for part in text.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start, end = part.split("-", 1)
                start, end = int(start), int(end)
                if start < 0 or end < start or end - start > 4096:
                    return set()
                result.update(range(start, end + 1))
            else:
                value = int(part)
                if value < 0:
                    return set()
                result.add(value)
    except (TypeError, ValueError):
        return set()
    return result


def _cpu_count():
    online = _cpu_ids(_read("/sys/devices/system/cpu/online"))
    if online:
        return len(online)
    try:
        text = _read("/proc/cpuinfo")
        count = sum(1 for line in text.splitlines() if re.match(r"^processor\s*:", line, re.I))
        return count or None
    except Exception:
        return None


def _mhz(path):
    raw = _read(path)
    try:
        value = float(raw)
        if value <= 0:
            return None
        # The cpufreq sysfs ABI reports kHz, including low MHz values.
        value /= 1000.0
        return "%.0f MHz" % value
    except (TypeError, ValueError):
        return None


def _proc_mhz(field):
    try:
        for line in _read("/proc/cpuinfo").splitlines():
            if line.lower().startswith(field.lower() + "\t") or line.lower().startswith(field.lower() + " "):
                value = line.split(":", 1)[1].strip()
                return _mhz_value(value)
    except (IndexError, ValueError):
        pass
    return None


def _mhz_value(raw):
    try:
        value = float(raw)
        return "%.0f MHz" % value if value > 0 else None
    except (TypeError, ValueError):
        return None


def cpu_info():
    rows = []
    count = _cpu_count()
    rows.append((_("Kerne"), str(count) if count is not None else UNAVAILABLE))
    current = _mhz("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
    if current is None:
        current = _proc_mhz("cpu MHz")
    maximum = _mhz("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")
    rows.append((_("Aktueller Takt"), current or UNAVAILABLE))
    rows.append((_("Maximaler Takt"), maximum or UNAVAILABLE))
    try:
        fields = _read("/proc/loadavg").split()
        load = ", ".join(fields[:3]) if len(fields) >= 3 else UNAVAILABLE
    except Exception:
        load = UNAVAILABLE
    rows.append((_("Systemlast (1/5/15 Min.)"), load))
    return rows


class NetworkRates(object):
    """Calculate per-interface rates from cumulative sysfs byte counters."""
    def __init__(self, clock=None):
        self.clock = clock or getattr(time, "monotonic", time.time)
        self.previous = {}

    def sample(self, interface, rx, tx, now=None):
        try:
            rx, tx = int(rx), int(tx)
            if rx < 0 or tx < 0:
                raise ValueError()
            now = self.clock() if now is None else float(now)
        except (TypeError, ValueError, OverflowError):
            return UNAVAILABLE, UNAVAILABLE
        old = self.previous.get(interface)
        self.previous[interface] = (rx, tx, now)
        if old is None:
            return UNAVAILABLE, UNAVAILABLE
        old_rx, old_tx, old_now = old
        elapsed = now - old_now
        if elapsed <= 0:
            return UNAVAILABLE, UNAVAILABLE
        def rate(current, previous):
            if current < previous:
                return UNAVAILABLE
            return _("%.2f Mbit/s") % ((current - previous) * 8.0 / elapsed / 1000000.0)
        return rate(rx, old_rx), rate(tx, old_tx)


def network_info(sampler=None):
    try:
        interfaces = sorted(os.listdir("/sys/class/net"))
    except (IOError, OSError):
        return [(_("Netzwerk"), UNAVAILABLE)]
    rows = []
    for interface in interfaces:
        if interface == "lo":
            continue
        base = "/sys/class/net/" + interface
        carrier = _read(base + "/carrier")
        operstate = _read(base + "/operstate")
        if carrier == "1":
            status = _("Verbunden")
        elif carrier == "0" or operstate == "down":
            status = _("Getrennt")
        elif operstate:
            status = operstate
        else:
            status = UNAVAILABLE
        speed = _read(base + "/speed")
        try:
            speed_value = int(speed)
            speed_text = "%d Mbit/s" % speed_value if speed_value > 0 else UNAVAILABLE
        except (TypeError, ValueError):
            speed_text = UNAVAILABLE
        kind = "WLAN" if os.path.exists(base + "/wireless") else ("LAN" if os.path.exists(base + "/device") else _("Sonstige"))
        rows.append((interface, "%s · %s · %s" % (kind, status, speed_text)))
        if sampler is not None:
            rx = _read(base + "/statistics/rx_bytes")
            tx = _read(base + "/statistics/tx_bytes")
            receive, send = sampler.sample(interface, rx, tx)
            rows.append((_("%s – Empfangen") % interface, receive))
            rows.append((_("%s – Gesendet") % interface, send))
    return rows or [(_("Netzwerk"), UNAVAILABLE)]


def active_tuner_info(session):
    """Read signal metrics from the currently active service, without tuning."""
    nav = getattr(session, "nav", None)
    service = _safe_call(nav, "getCurrentService") if nav is not None else None
    frontend = _safe_call(service, "frontendInfo") if service is not None else None
    status = _safe_call(frontend, "getFrontendStatus") if frontend is not None else None
    if not isinstance(status, dict):
        return [(_("Signalqualität"), UNAVAILABLE), (_("AGC"), UNAVAILABLE),
                (_("BER"), UNAVAILABLE), (_("Tuner-Lock"), UNAVAILABLE)]

    def numeric(keys, suffix="", scale=1.0):
        for key in keys:
            if key not in status:
                continue
            try:
                value = float(status[key])
                if value < 0:
                    continue
                if suffix == "%":
                    value *= scale
                    if value > 100:
                        continue
                    return _("%.0f%%") % value
                if suffix == " dB":
                    value *= scale
                return (_("%.2f") % value).rstrip("0").rstrip(".") + _(suffix)
            except (TypeError, ValueError, OverflowError):
                continue
        return UNAVAILABLE

    snr = numeric(("tuner_signal_quality_db",), " dB", 0.01)
    if snr == UNAVAILABLE:
        snr = numeric(("snr_db", "SNR_dB"), " dB")
    if snr == UNAVAILABLE:
        snr = numeric(("snr_percent", "signal_quality"), "%")
    if snr == UNAVAILABLE:
        snr = numeric(("tuner_signal_quality", "snr", "signal", "SNR"), "%", 100.0 / 65535.0)
    agc = numeric(("tuner_signal_power", "agc", "AGC"), "%", 100.0 / 65535.0)
    ber = numeric(("tuner_bit_error_rate", "ber", "BER"))
    lock_value = status.get("tuner_locked", status.get("lock", status.get("LOCK")))
    if isinstance(lock_value, (int, float)):
        lock = _("Ja") if lock_value > 0 else (_("Nein") if lock_value == 0 else UNAVAILABLE)
    elif isinstance(lock_value, bool):
        lock = _("Ja") if lock_value else _("Nein")
    else:
        lock = UNAVAILABLE
    return [(_("Signalqualität"), snr), (_("AGC"), agc),
            (_("BER"), ber), (_("Tuner-Lock"), lock)]


def _safe_call(obj, name, *args):
    try:
        method = getattr(obj, name)
        return method(*args)
    except Exception:
        return None


def _frontend_infos(frontend_info):
    if frontend_info is None:
        return []
    values = _safe_call(frontend_info, "getAll", True)
    if values is None:
        values = _safe_call(frontend_info, "getAll")
    if values is None:
        return []
    if isinstance(values, dict):
        values = [values]
    try:
        return list(values)
    except TypeError:
        return []


def _frontend_number(info):
    if isinstance(info, dict):
        for key in ("tuner_number", "tunerNumber", "frontend_id", "frontendId"):
            value = info.get(key)
            if value is not None:
                try:
                    return int(value)
                except (TypeError, ValueError):
                    pass
    for key in ("tuner_number", "tunerNumber", "frontend_id", "frontendId"):
        value = getattr(info, key, None)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    return None


def _slot_label(slot):
    try:
        name = str(getattr(slot, "name", "") or getattr(slot, "description", "") or
                   getattr(slot, "friendly_full_description", "") or "")
    except Exception:
        name = ""
    try:
        types = getattr(slot, "getSlotType", None)
        kind = types() if callable(types) else getattr(slot, "type", "")
        kind = str(kind or "")
    except Exception:
        kind = ""
    if not kind or kind.lower() in ("none", "unknown", "0"):
        return ""
    if name and kind.lower() not in name.lower():
        return "%s (%s)" % (name[:28], kind[:24])
    return (name or kind)[:52]


def _slot_number(slot, fallback):
    for key in ("slot", "slotid", "slot_id", "frontend_id", "tuner_number"):
        value = getattr(slot, key, None)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                pass
    return fallback


def _recordings(nav):
    """Return (items, count, count_source): real, timer, or None."""
    try:
        from enigma import pNavigation
        real_recording = pNavigation.isRealRecording
    except Exception:
        real_recording = None
    if real_recording is not None:
        try:
            values = nav.getRecordings(False, real_recording)
            values = list(values)
            return values, len(values), "real"
        except Exception:
            pass
        # Some images expose the native pNavigation overload while their
        # Python Navigation wrapper only accepts the simulate argument.
        native_nav = getattr(nav, "pnav", None)
        try:
            values = native_nav.getRecordings(False, real_recording)
            values = list(values)
            return values, len(values), "real"
        except Exception:
            pass
    try:
        values = nav.getRecordings(False)
        values = list(values)
    except Exception:
        values = None
    # On OpenPLi the public wrapper filters StreamServiceList, but does not
    # offer the real-recording filter. Its RecordTimer list gives a separate,
    # explicitly labelled count of running non-zap timers.
    timer_count = _timer_recording_count(nav)
    if timer_count is not None:
        return values, timer_count, "timer"
    # The one-argument recording list can include services that are not
    # genuine recordings on other images, so do not present its length.
    return values, None, None


def _timer_recording_count(nav):
    try:
        record_timer = getattr(nav, "RecordTimer")
        timer_list = list(getattr(record_timer, "timer_list"))
    except Exception:
        return None
    count = 0
    for entry in timer_list:
        try:
            is_running = getattr(entry, "isRunning")
            justplay = getattr(entry, "justplay")
            if not callable(is_running):
                return None
            if is_running() and not justplay:
                count += 1
        except Exception:
            return None
    return count


def tuner_info(session):
    rows = []
    slots = None
    try:
        from Components.NimManager import nimmanager
        slots = getattr(nimmanager, "nim_slots", None)
    except Exception:
        slots = None
    if slots is None:
        rows.append((_("Konfigurierte Tuner"), UNAVAILABLE))
    else:
        try:
            slots = list(slots)
        except TypeError:
            slots = []
        rows.append((_("Konfigurierte Tuner"), str(len(slots))))

    occupied = set()
    recordings = None
    recording_count = None
    count_source = None
    try:
        nav = getattr(session, "nav", None)
        service = _safe_call(nav, "getCurrentService") if nav is not None else None
        info = _safe_call(service, "frontendInfo") if service is not None else None
        for frontend in _frontend_infos(info):
            number = _frontend_number(frontend)
            if number is not None:
                occupied.add(number)
        recordings, recording_count, count_source = _recordings(nav) if nav is not None else (None, None, None)
        if recordings is not None:
            for recordservice in recordings:
                rec_info = _safe_call(recordservice, "frontendInfo")
                for frontend in _frontend_infos(rec_info):
                    number = _frontend_number(frontend)
                    if number is not None:
                        occupied.add(number)
    except Exception:
        recording_count = None
        recordings = None
        count_source = None
    if recording_count is not None and count_source == "real":
        count_text = str(recording_count)
        count_label = _("Laufende Aufnahmen")
    elif recording_count is not None and count_source == "timer":
        count_text = str(recording_count)
        count_label = _("Aufnahmen (Timer)")
    elif recordings is not None:
        count_text = _("Nicht unterscheidbar")
        count_label = _("Laufende Aufnahmen")
    else:
        count_text = UNAVAILABLE
        count_label = _("Laufende Aufnahmen")
    rows.append((count_label, count_text))

    if slots is not None:
        configured = [(slot, _slot_number(slot, index), _slot_label(slot))
                      for index, slot in enumerate(slots)]
        configured = [(slot, number, label) for slot, number, label in configured if label]
        rows[0] = (_("Tuner-Frontends"), str(len(configured)))
        for slot, number, label in configured:
            marker = _("Aktiv") if number in occupied else _("Keine aktive Nutzung erkannt")
            rows.append(("Tuner %d" % number, "%s · %s" % (label, marker)))
    if not occupied and slots is None:
        rows.append((_("Tunerbelegung"), UNAVAILABLE))
    elif occupied and slots is None:
        rows.append((_("Belegte Frontends"), ", ".join(str(value) for value in sorted(occupied))))
    return rows
