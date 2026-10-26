# -*- coding: utf-8 -*-
"""Lightweight Enigma2 system information plugin (Python 2/3 syntax intended; runtime validation required)."""

from __future__ import print_function

import os
import platform
import re
import time
import glob
import json

from .probes import cpu_info, network_info, tuner_info

from enigma import eConsoleAppContainer, eTimer

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigSelection, configfile
from Plugins.Plugin import PluginDescriptor

try:
    from enigma import gRGB
except ImportError:
    gRGB = None


if not hasattr(config.plugins, "boxsysteminfo"):
    config.plugins.boxsysteminfo = ConfigSubsection()
config.plugins.boxsysteminfo.theme = ConfigSelection(
    default="midnight",
    choices=[("midnight", "Midnight"), ("ocean", "Ocean"), ("amber", "Amber"), ("light", "Light")]
)


VERSION = "0.1.9"

# Advisory display thresholds, not hardware manufacturer limits.
SOC_WARNING = 80.0
DRIVE_WARNING = 60.0
STORAGE_WARNING = 90

THEMES = {
    "midnight": {"bg": "#101722", "panel": "#1b2938", "accent": "#50d6a3", "text": "#f1f5f9", "muted": "#aab8c7", "name": "Midnight"},
    "ocean":    {"bg": "#071d2b", "panel": "#10384b", "accent": "#47c8e8", "text": "#effbff", "muted": "#a9d2df", "name": "Ocean"},
    "amber":    {"bg": "#21170d", "panel": "#3a2918", "accent": "#ffbd59", "text": "#fff8ed", "muted": "#dec7a8", "name": "Amber"},
    "light":    {"bg": "#e9eef3", "panel": "#ffffff", "accent": "#087f69", "text": "#15212b", "muted": "#52616c", "name": "Light"},
}


def _read(path, default="—"):
    try:
        with open(path, "r") as handle:
            value = handle.read().strip()
        return value or default
    except (IOError, OSError):
        return default


def _first_line(path, default="—"):
    value = _read(path, default)
    return value.splitlines()[0] if value != default else default


def _pretty_bytes(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0 or unit == "TB":
            return "%.1f %s" % (value, unit)
        value /= 1024.0
    return "—"


def _memory_info():
    values = {}
    try:
        with open("/proc/meminfo", "r") as handle:
            for line in handle:
                match = re.match(r"^(MemTotal|MemAvailable|MemFree|Buffers|Cached):\s+(\d+)", line)
                if match:
                    values[match.group(1)] = int(match.group(2)) * 1024
    except (IOError, OSError):
        return "—", "—"
    total = values.get("MemTotal")
    available = values.get("MemAvailable")
    if available is None:
        available = sum(values.get(key, 0) for key in ("MemFree", "Buffers", "Cached"))
    if not total:
        return "—", "—"
    used = max(0, total - available)
    return "%s / %s" % (_pretty_bytes(used), _pretty_bytes(total)), "%d%% belegt" % int(used * 100 / total)


def _uptime():
    try:
        seconds = int(float(_read("/proc/uptime", "0").split()[0]))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes = seconds // 60
        if days:
            return "%d Tage, %d Std., %d Min." % (days, hours, minutes)
        return "%d Std., %d Min." % (hours, minutes)
    except (ValueError, IndexError):
        return "—"


def _cpu_name():
    try:
        with open("/proc/cpuinfo", "r") as handle:
            for line in handle:
                if line.lower().startswith(("model name", "hardware", "processor")) and ":" in line:
                    value = line.split(":", 1)[1].strip()
                    if value and not value.isdigit():
                        return value
    except (IOError, OSError):
        pass
    return platform.machine() or "—"


def _box_model():
    # VU+ exposes its real product name separately on many images. Generic
    # compatibility values in /proc/stb/info/model can misleadingly say dm8000.
    for path in ("/proc/stb/info/vumodel", "/proc/stb/info/hwmodel",
                 "/proc/stb/info/model", "/proc/stb/info/boxtype"):
        value = _read(path, "")
        if value:
            normalized = re.sub(r"[^a-z0-9]", "", value.lower())
            if normalized in ("uno4kse", "vuuno4kse"):
                return "Vu+ Uno 4K SE"
            if normalized in ("uno4k", "vuuno4k"):
                return "Vu+ Uno 4K"
            if normalized.startswith("vu"):
                return "Vu+ " + value[2:].strip(" _-").upper()
            return value
    return platform.node() or "—"


def _format_temperature(raw, millidegrees=False):
    try:
        value = float(raw.strip())
        if millidegrees:
            value /= 1000.0
        # Some vendor proc nodes report milli-degrees despite not documenting it.
        elif value > 200:
            value /= 1000.0
        if value < -20 or value > 150:
            return None
        return "%.1f°C" % value
    except (AttributeError, TypeError, ValueError):
        return None


def _soc_temperature():
    # Vendor proc interfaces first, then the standard Linux thermal sysfs ABI.
    candidates = (
        ("/proc/stb/fp/temp_sensor_avs", False),
        ("/proc/stb/sensors/temp0/value", False),
        ("/proc/stb/sensors/temp/value", False),
        ("/proc/stb/fp/temp_sensor", False),
        ("/sys/devices/virtual/thermal/thermal_zone0/temp", True),
        ("/sys/class/thermal/thermal_zone0/temp", True),
    )
    for path, milli in candidates:
        result = _format_temperature(_read(path, ""), milli)
        if result:
            return result
    try:
        text = _read("/proc/hisi/msp/pm_cpu", "")
        match = re.search(r"temperature\s*=\s*(\d+)", text, re.I)
        if match:
            return _format_temperature(match.group(1))
    except Exception:
        pass
    # Some images expose the same thermal zone under hwmon only.
    for path in sorted(glob.glob("/sys/class/hwmon/hwmon*/temp*_input")):
        labels = glob.glob(os.path.join(os.path.dirname(path), "temp*_label"))
        label = ""
        if labels:
            label = _read(labels[0], "").lower()
        name = _read(os.path.join(os.path.dirname(path), "name"), "").lower()
        if any(token in (label + " " + name) for token in ("cpu", "soc", "bcm", "avs")):
            result = _format_temperature(_read(path, ""), True)
            if result:
                return result
    return "Nicht verfügbar"


def _find_executable(name):
    directories = [os.path.join(os.path.dirname(__file__), "bin")]
    directories += os.environ.get("PATH", "").split(os.pathsep)
    directories += ["/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/sbin", "/usr/bin", "/bin"]
    for directory in directories:
        if not directory or not os.path.isabs(directory):
            continue
        candidate = os.path.join(directory, name)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def _drive_devices():
    return [path for path in sorted(glob.glob("/sys/block/*"))
            if re.match(r"^(sd[a-z]+|hd[a-z]+|nvme[0-9]+n[0-9]+)$", os.path.basename(path))]


def _drive_hwmon(devices):
    for device in devices:
        for path in sorted(glob.glob(os.path.join(device, "device/hwmon/hwmon*/temp*_input"))):
            result = _format_temperature(_read(path, ""), True)
            if result:
                return "%s (%s)" % (result, os.path.basename(device))
    for path in sorted(glob.glob("/sys/class/hwmon/hwmon*/temp*_input")):
        directory = os.path.dirname(path)
        label = _read(path.replace("_input", "_label"), "")
        name = _read(os.path.join(directory, "name"), "")
        if any(token in (label + " " + name).lower() for token in ("ssd", "nvme", "hdd", "disk", "drivetemp")):
            result = _format_temperature(_read(path, ""), True)
            if result:
                return result
    return None


def _parse_smart_temperature(output):
    raw_index = None
    for line in output.splitlines():
        columns = line.split()
        if "ATTRIBUTE_NAME" in columns and "RAW_VALUE" in columns:
            raw_index = columns.index("RAW_VALUE")
            continue
        # ATA tables: use RAW_VALUE, never normalized VALUE/WORST/THRESH.
        if columns and columns[0].isdigit() and len(columns) > 1:
            if "temperature" in columns[1].lower():
                index = raw_index if raw_index is not None else 9
                if len(columns) > index:
                    match = re.match(r"^(-?[0-9]+(?:\.[0-9]+)?)(?:$|[^0-9.])", columns[index])
                    if match:
                        result = _format_temperature(match.group(1))
                        if result:
                            return result
        # NVMe and SCSI text formats.
        match = re.match(r"^\s*(?:Current Drive )?Temperature:\s*(-?[0-9]+(?:\.[0-9]+)?)\s*(Celsius|Kelvin|K|°C)?", line, re.I)
        if match:
            value = float(match.group(1))
            if (match.group(2) or "").lower() in ("kelvin", "k"):
                value -= 273.15
            result = _format_temperature(str(value))
            if result:
                return result
    return None


def _parse_smart_details(output, retval=0):
    details = {}
    raw_index = 9
    for line in output.splitlines():
        match = re.match(r"^\s*(?:Device Model|Model Number|Product):\s*(.+?)\s*$", line)
        if match:
            details["model"] = match.group(1)
        match = re.search(r"(?:SMART overall-health self-assessment test result|SMART Health Status):\s*(.+)", line, re.I)
        if match:
            status = match.group(1).strip().upper()
            if status in ("PASSED", "OK"):
                details["health"] = "Bestanden"
            elif "FAIL" in status or "BAD" in status:
                details["health"] = "Fehlgeschlagen"
                details["health_failed"] = True
            else:
                details["health"] = "Nicht eindeutig"
        columns = line.split()
        if "ATTRIBUTE_NAME" in columns and "RAW_VALUE" in columns:
            raw_index = columns.index("RAW_VALUE")
        if len(columns) > raw_index and columns[0].isdigit() and columns[1] in ("Power_On_Hours", "Power_On_Hours_and_Msec"):
            match = re.match(r"^([0-9]+)", columns[raw_index])
            if match:
                details["hours"] = match.group(1) + " Std."
        match = re.match(r"^\s*Power On Hours:\s*([0-9][0-9,]*)", line, re.I)
        if match:
            details["hours"] = match.group(1).replace(",", "") + " Std."
    if retval >= 0 and retval & 8:
        details["health"] = "Fehlgeschlagen"
        details["health_failed"] = True
    return details


def _recording_path():
    try:
        value = config.usage.default_path.value
        if value and os.path.isabs(value):
            return value
    except (AttributeError, TypeError):
        pass
    try:
        from Components.Harddisk import harddiskmanager
        paths = set()
        for partition in harddiskmanager.getMountedPartitions():
            value = getattr(partition, "mountpoint", "")
            if value and os.path.isabs(value) and value.rstrip("/"):
                paths.add(value.rstrip("/"))
        if len(paths) == 1:
            return paths.pop()
    except (ImportError, AttributeError, TypeError, OSError, RuntimeError):
        pass
    return ""


def _temperature_warning(value, threshold):
    match = re.search(r"(-?[0-9]+(?:\.[0-9]+)?)\s*°C", value or "")
    return bool(match and float(match.group(1)) >= threshold)


def _root_usage():
    try:
        stats = os.statvfs("/")
        total = stats.f_blocks * stats.f_frsize
        free = stats.f_bavail * stats.f_frsize
        used = (stats.f_blocks - stats.f_bfree) * stats.f_frsize
        percent = int(100.0 * used / (used + free)) if used + free else 0
        return {"total": total, "free": free, "used": used, "percent": percent}
    except (OSError, AttributeError):
        return {}


class DriveTemperatureQuery(object):
    """One read-only query at a time, driven entirely by the Enigma2 event loop."""
    def __init__(self, callback, preferred_device=None):
        self.callback = callback
        self.preferred_device = preferred_device
        self.details = {}
        self._fallback_details = {}
        self.selected_device = None
        self.container = None
        self.timer = eTimer()
        self.timer_connection = None
        try:
            self.timer.callback.append(self._timeout)
        except AttributeError:
            self.timer_connection = self.timer.timeout.connect(self._timeout)
        self.active = False
        self.output = ""
        self.devices = []
        self.pending = []
        self.status = "Keine Temperaturdaten"
        self.attempts = 0

    def start(self):
        self.active = True
        self.devices = _drive_devices()
        if self.preferred_device:
            match = re.match(r"^/dev/(sd[a-z]+|hd[a-z]+|nvme[0-9]+n[0-9]+)(?:p?[0-9]+)?$", self.preferred_device)
            if match:
                preferred = match.group(1)
                self.selected_device = preferred
                self.devices.sort(key=lambda path: os.path.basename(path) != preferred)
        self.smartctl = _find_executable("smartctl")
        if not self.smartctl:
            self._finish("smartctl fehlt")
            return
        self.pending = [(os.path.basename(path), None) for path in self.devices[:4]]
        self._next()

    def _next(self):
        if not self.active:
            return
        if not self.pending or self.attempts >= 4:
            if not self.details:
                self.details = self._fallback_details
            self._finish(self.status if self.devices else "Kein Laufwerk gefunden")
            return
        self.device, self.device_type = self.pending.pop(0)
        self.attempts += 1
        self.output = ""
        self.timed_out = False
        self.container = eConsoleAppContainer()
        self.container.dataAvail.append(self._data)
        self.container.appClosed.append(self._closed)
        args = [self.smartctl, self.smartctl, "-n", "standby,3", "-i", "-H", "-A"]
        if self.device_type:
            args.extend(["-d", self.device_type])
        args.append("/dev/" + self.device)
        self.timer.start(3000, True)
        try:
            failed = self.container.execute(*args)
        except (OSError, RuntimeError, TypeError):
            failed = True
        if failed:
            self._closed(1)

    def _data(self, data):
        if not isinstance(data, str):
            data = data.decode("utf-8", "replace")
        # Bound memory, and never print complete SMART output or identifiers.
        self.output = (self.output + data)[:65536]

    def _detach(self):
        self.timer.stop()
        container = self.container
        self.container = None
        if container is not None:
            container.dataAvail.remove(self._data)
            container.appClosed.remove(self._closed)
        return container

    def _closed(self, retval):
        if self.container is None:
            return
        self._detach()
        if not self.active:
            return
        self.details = {} if self.timed_out else _parse_smart_details(self.output, retval)
        if self.details:
            self.details["device"] = "/dev/" + self.device
        temperature = None if self.timed_out else _parse_smart_temperature(self.output)
        if temperature:
            self._finish("%s (%s, SMART)" % (temperature, self.device), available=True)
            return
        lower = self.output.lower()
        if self.timed_out:
            self.status = "SMART-Zeitlimit erreicht"
        elif "standby" in lower or "sleep mode" in lower:
            self.status = "Laufwerk im Standby"
        elif not self.device_type and "-d" in lower and ("specify" in lower or "unknown usb bridge" in lower):
            # Retry SAT only when smartctl explicitly requests a device type.
            self.pending.insert(0, (self.device, "sat"))
            self.status = "SMART-Gerätetyp nicht erkannt"
        elif retval & 7:
            self.status = "SMART-Abfrage fehlgeschlagen"
        else:
            self.status = "Keine SMART-Temperaturdaten"
        retry_type = self.pending[:1] == [(self.device, "sat")]
        if self.selected_device == self.device and not retry_type:
            self._finish(self.status)
        else:
            if self.details and not self._fallback_details:
                self._fallback_details = self.details
            self.details = {}
            self._next()

    def _timeout(self):
        if self.container is not None:
            self.timed_out = True
            # OpenPLi kill() closes pipes without guaranteeing appClosed.
            container = self._detach()
            container.kill()
            self.status = "SMART-Zeitlimit erreicht"
            self._next()

    def _finish(self, value, available=False):
        self.active = False
        self.timer.stop()
        if not available:
            value = _drive_hwmon(self.devices) or value
        self.callback(value)

    def cancel(self):
        self.active = False
        container = self._detach()
        if container is not None:
            container.kill()
        self.callback = None


class StorageQuery(DriveTemperatureQuery):
    def start(self, path):
        self.active = True
        self.output = ""
        if not path or not os.path.isabs(path):
            self._finish({"status": "Kein Aufnahmepfad ermittelt"})
            return
        python = _find_executable("python3") or _find_executable("python")
        if python is None:
            self._finish({"status": "Python-Werkzeug fehlt"})
            return
        self.container = eConsoleAppContainer()
        self.container.dataAvail.append(self._data)
        self.container.appClosed.append(self._closed)
        self.timer.start(3000, True)
        try:
            failed = self.container.execute(python, python, os.path.join(os.path.dirname(__file__), "storage.py"), path)
        except (OSError, TypeError, RuntimeError):
            failed = True
        if failed:
            self._closed(1)

    def _closed(self, retval):
        if self.container is None:
            return
        self._detach()
        try:
            result = json.loads(self.output) if retval == 0 else {}
            if not isinstance(result, dict):
                result = {}
        except (ValueError, TypeError):
            result = {}
        self._finish(result or {"status": "Speicherabfrage fehlgeschlagen"})

    def _timeout(self):
        if self.container is not None:
            container = self._detach()
            container.kill()
            self._finish({"status": "Speicherabfrage: Zeitlimit erreicht"})

    def _finish(self, result, available=False):
        self.active = False
        self.timer.stop()
        self.callback(result)


def _metadata_value(value):
    if value is None or isinstance(value, bool):
        return ""
    value = str(value).strip()
    return "" if value.lower() in ("", "none", "unknown", "n/a", "unavailable", "undefined") else value


def _image_info():
    image = {}
    # enigma.info is the actual BoxInfo source on current OpenPLi/OpenATV.
    for path in ("/etc/os-release", "/etc/image-version", "/usr/lib/enigma.info"):
        for line in _read(path, "").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                value = _metadata_value(value.strip().strip("'\""))
                if value:
                    image[key.strip().lower().replace("-", "_")] = value
    try:
        from Components.SystemInfo import BoxInfo
        for key in ("displaydistro", "distro", "imageversion", "imagebuild", "imgversion", "imgrevision"):
            value = _metadata_value(BoxInfo.getItem(key))
            if value:
                image[key] = value
    except (ImportError, AttributeError, TypeError, RuntimeError):
        pass
    try:
        import boxbranding
        for key, function in (("displaydistro", "getImageDistro"), ("imageversion", "getImageVersion"), ("imagebuild", "getImageBuild")):
            value = _metadata_value(getattr(boxbranding, function, lambda: "")())
            if value:
                image.setdefault(key, value)
    except (ImportError, AttributeError, TypeError, RuntimeError):
        pass
    issue = _first_line("/etc/issue", "").replace("\\n", "").replace("\\l", "").strip()
    name = (image.get("displaydistro") or image.get("imagename") or image.get("image_name")
            or image.get("name") or image.get("distro") or image.get("id") or issue or "Enigma2 Image")
    version = (image.get("imageversion") or image.get("image_version") or image.get("imgversion")
               or image.get("version_id") or image.get("version") or "—")
    build = image.get("imagebuild") or image.get("image_build") or image.get("imgrevision") or image.get("build_id") or image.get("build") or ""
    return name, version, build


def _image_build_date():
    value = ""
    try:
        from Components.SystemInfo import BoxInfo
        value = _metadata_value(BoxInfo.getItem("compiledate"))
    except (ImportError, AttributeError, TypeError, RuntimeError):
        pass
    if not value:
        for line in _read("/usr/lib/enigma.info", "").splitlines():
            if "=" in line and line.split("=", 1)[0].strip() == "compiledate":
                value = line.split("=", 1)[1].strip().strip("'\"")
                break
    if re.match(r"^[0-9]{8}$", value):
        try:
            return time.strftime("%d.%m.%Y", time.strptime(value, "%Y%m%d"))
        except ValueError:
            pass
    return "—"


def _enigma_version():
    try:
        from enigma import getEnigmaVersionString
        value = _metadata_value(getEnigmaVersionString())
        if value:
            return value
    except (ImportError, AttributeError, TypeError, RuntimeError):
        pass
    try:
        from Components.About import about
        return _metadata_value(about.getEnigmaVersionString()) or "—"
    except (ImportError, AttributeError, TypeError, RuntimeError):
        return "—"


def _disk_info():
    try:
        stats = os.statvfs("/")
        total = stats.f_blocks * stats.f_frsize
        free = stats.f_bavail * stats.f_frsize
        return "%s frei von %s" % (_pretty_bytes(free), _pretty_bytes(total))
    except (AttributeError, OSError):
        return "—"


def _systeminfo_skin():
    # Fixed HD canvas, standard Enigma2 Labels only; no image assets or renderers.
    widgets = []

    def label(name, x, y, width, height, font, opaque=False):
        widgets.append('<widget name="%s" position="%d,%d" size="%d,%d" font="Regular;%d" transparent="%d" zPosition="%d" />' %
                       (name, x, y, width, height, font, 0 if opaque else 1, 0 if opaque else 1))

    label("heading", 38, 25, 820, 48, 34)
    label("release", 926, 35, 150, 30, 20)
    label("subheading", 40, 79, 1030, 32, 20)
    for name, x in (("temperature", 36), ("memory", 390), ("storage", 744)):
        label(name + "_panel", x, 132, 340, 138, 20, True)
        label(name + "_title", x + 18, 146, 304, 28, 20)
        label(name + "_value", x + 18, 180, 304, 38, 25)
        label(name + "_detail", x + 18, 224, 304, 28, 19)
    label("boxpanel", 36, 288, 518, 270, 20, True)
    label("imagepanel", 572, 288, 512, 270, 20, True)
    label("boxhead", 54, 300, 470, 32, 23)
    label("imagehead", 590, 300, 470, 32, 23)
    for index in range(4):
        y = 350 + index * 46
        label("box_label_%d" % index, 54, y, 158, 32, 19)
        label("box_value_%d" % index, 216, y, 320, 38, 20)
    for index in range(8):
        y = 342 + index * 25
        label("image_label_%d" % index, 590, y, 148, 26, 18)
        label("image_value_%d" % index, 740, y, 326, 26, 19)
    label("footer", 40, 589, 1040, 32, 19)
    return '<screen name="BoxSystemInfo" position="center,center" size="1120,650" title="Box Systeminfo">%s</screen>' % "".join(widgets)


class BoxSystemInfo(Screen):
    skin = _systeminfo_skin()

    def __init__(self, session):
        Screen.__init__(self, session)
        self["heading"] = Label("Box Systeminfo")
        self["release"] = Label("Version " + VERSION)
        self["subheading"] = Label("Receiver und Image auf einen Blick")
        self["boxhead"] = Label("Receiver")
        self["imagehead"] = Label("Image und System")
        self["boxpanel"] = Label("")
        self["imagepanel"] = Label("")
        self["footer"] = Label("")
        for name, title in (("temperature", "Temperaturen"), ("memory", "Arbeitsspeicher"), ("storage", "Root-Speicher")):
            for suffix in ("panel", "title", "value", "detail"):
                self[name + "_" + suffix] = Label(title if suffix == "title" else "")
        for prefix, count in (("box", 4), ("image", 8)):
            for index in range(count):
                self["%s_label_%d" % (prefix, index)] = Label("")
                self["%s_value_%d" % (prefix, index)] = Label("")
        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions"], {
            "cancel": self.close,
            "ok": self.refresh,
            "left": self.previous_theme,
            "right": self.next_theme,
            "green": self.next_theme,
            "red": self.close,
            "yellow": self.show_details,
            "blue": self.show_details,
            "menu": self.show_help,
        }, -1)
        self._drive_query = None
        self._storage_query = None
        self._details_screen = None
        self._recording = {"status": "Wird gelesen …"}
        self._drive_details = {}
        self._root = {}
        self._drive_value = "Wird gelesen …"
        self.onClose.append(self._cancel_drive_query)
        self.onLayoutFinish.append(self.apply_theme)
        self.refresh()
        self.apply_theme()

    def _cancel_drive_query(self):
        if self._storage_query is not None:
            self._storage_query.cancel()
            self._storage_query = None
        if self._drive_query is not None:
            self._drive_query.cancel()
            self._drive_query = None

    def _drive_result(self, value):
        self._drive_value = value
        self._drive_details = self._drive_query.details if self._drive_query else {}
        self._render_box()
        self.apply_theme()
        self._notify_details()

    def _recording_result(self, result):
        self._recording = result
        self._drive_query = DriveTemperatureQuery(self._drive_result, result.get("device"))
        self._drive_query.start()
        self.apply_theme()
        self._notify_details()

    def _notify_details(self):
        if self._details_screen is not None:
            self._details_screen.render()

    def _details_closed(self, *args):
        self._details_screen = None

    def show_details(self):
        self._details_screen = self.session.openWithCallback(self._details_closed, SystemDetails, self)

    def detail_pages(self):
        recording = self._recording
        drive = self._drive_details
        missing = "Nicht verfügbar"
        storage_rows = [
            ("Abfragepfad", recording.get("path") or _recording_path() or missing),
            ("Speicherstatus", recording.get("status", missing)),
            ("Einhängepunkt", recording.get("mount", missing)),
            ("Kapazität", _pretty_bytes(recording.get("total"))),
            ("Belegt", _pretty_bytes(recording.get("used"))),
            ("Frei", _pretty_bytes(recording.get("free"))),
            ("Speicherbelegung", "%s%%" % recording["percent"] if "percent" in recording else missing),
            ("SMART-Gerät", drive.get("device", missing)),
            ("Laufwerksmodell", drive.get("model", missing)),
            ("SMART-Gesamtstatus", drive.get("health", missing)),
            ("Betriebsstunden", drive.get("hours", missing)),
            ("Laufwerkstemperatur", self._drive_value.split(" (", 1)[0]),
        ]
        pages = []
        for title, rows in (("Aufnahmespeicher und Laufwerk", storage_rows), ("Prozessor", self._cpu_rows),
                            ("Netzwerk", self._network_rows), ("Tuner und Aufnahmen", self._tuner_rows)):
            for offset in range(0, len(rows), 12):
                pages.append((title, rows[offset:offset + 12]))
        return pages

    def _render_box(self):
        for index, (key, value) in enumerate(self._box_rows):
            self["box_label_%d" % index].setText(key)
            self["box_value_%d" % index].setText(value)
        self["temperature_value"].setText("SoC  " + self._soc_value)
        # Keep the temperature prominent and long failure messages readable.
        drive = self._drive_value.split(" (", 1)[0]
        self["temperature_detail"].setText("SSD  " + drive)

    def refresh(self):
        self._cancel_drive_query()
        self._drive_value = "Wird gelesen …"
        self._drive_details = {}
        self._recording = {"status": "Wird gelesen …"}
        self._cpu_rows = cpu_info()
        self._network_rows = network_info()
        self._tuner_rows = tuner_info(self.session)
        image_name, image_version, image_build = _image_info()
        memory, memory_percent = _memory_info()
        model = _box_model()
        version = _enigma_version()
        kernel = platform.release() or "—"
        python_version = platform.python_version()
        self._box_rows = [
            ("Modell", model),
            ("Prozessor", _cpu_name()),
            ("Architektur", platform.machine() or "—"),
            ("Systemlaufzeit", _uptime()),
        ]
        self._soc_value = _soc_temperature()
        self._memory_warning = bool(re.match(r"^(9[0-9]|100)%", memory_percent))
        self["memory_value"].setText(memory_percent)
        self["memory_detail"].setText(memory)
        self._root = _root_usage()
        self["storage_value"].setText(_pretty_bytes(self._root.get("free")) + " frei")
        self["storage_detail"].setText("von " + _pretty_bytes(self._root.get("total")))
        image_rows = [
            ("Image", image_name),
            ("Image-Version", image_version),
            ("Build", image_build or "—"),
            ("Image erstellt", _image_build_date()),
            ("Enigma2", version),
            ("Kernel", kernel),
            ("Python", python_version),
            ("Aktualisiert", time.strftime("%H:%M:%S")),
        ]
        self._render_box()
        self._storage_query = StorageQuery(self._recording_result)
        self._storage_query.start(_recording_path())
        for index, (key, value) in enumerate(image_rows):
            self["image_label_%d" % index].setText(key)
            self["image_value_%d" % index].setText(value)
        theme = THEMES.get(config.plugins.boxsysteminfo.theme.value, THEMES["midnight"])
        self["footer"].setText("◀ / ▶ %s    OK Aktualisieren    GELB Details    MENU Hilfe    EXIT Schließen" % theme["name"])
        self.apply_theme()
        self._notify_details()

    def _set_color(self, widget, color, foreground=False):
        if gRGB is None or widget.instance is None:
            return
        try:
            rgb = int(color.lstrip("#"), 16)
            value = gRGB(rgb)
            if foreground:
                widget.instance.setForegroundColor(value)
            else:
                widget.instance.setBackgroundColor(value)
        except Exception:
            pass

    def apply_theme(self):
        theme = THEMES.get(config.plugins.boxsysteminfo.theme.value, THEMES["midnight"])
        if self.instance is not None:
            self._set_color(self, theme["bg"])
        panels = ["boxpanel", "imagepanel"] + [name + "_panel" for name in ("temperature", "memory", "storage")]
        for key in panels:
            self._set_color(self[key], theme["panel"])
        for name in ("temperature", "memory", "storage"):
            for suffix in ("title", "value", "detail"):
                self._set_color(self[name + "_" + suffix], theme["panel"])
            self._set_color(self[name + "_title"], theme["muted"], True)
            self._set_color(self[name + "_value"], theme["accent"], True)
            self._set_color(self[name + "_detail"], theme["text"], True)
        for prefix, count in (("box", 4), ("image", 8)):
            for index in range(count):
                self._set_color(self["%s_label_%d" % (prefix, index)], theme["panel"])
                self._set_color(self["%s_value_%d" % (prefix, index)], theme["panel"])
                self._set_color(self["%s_label_%d" % (prefix, index)], theme["muted"], True)
                self._set_color(self["%s_value_%d" % (prefix, index)], theme["text"], True)
        for key in ("heading", "boxhead", "imagehead"):
            self._set_color(self[key], theme["bg"] if key == "heading" else theme["panel"])
            self._set_color(self[key], theme["text"], True)
        for key in ("subheading", "footer", "release"):
            self._set_color(self[key], theme["bg"])
            self._set_color(self[key], theme["muted"], True)
        self._set_color(self["temperature_value"], "#e46969" if _temperature_warning(self._soc_value, SOC_WARNING) else theme["accent"], True)
        self._set_color(self["temperature_detail"], "#e46969" if _temperature_warning(self._drive_value, DRIVE_WARNING) else theme["text"], True)
        self._set_color(self["memory_value"], "#e46969" if self._memory_warning else theme["accent"], True)
        self._set_color(self["storage_value"], "#e46969" if self._root.get("percent", 0) >= STORAGE_WARNING else theme["accent"], True)
        if self._drive_details.get("health_failed"):
            self._set_color(self["temperature_detail"], "#e46969", True)
        if self.instance is not None:
            self.instance.invalidate()

    def _change_theme(self, delta):
        keys = ["midnight", "ocean", "amber", "light"]
        current = config.plugins.boxsysteminfo.theme.value
        index = keys.index(current) if current in keys else 0
        config.plugins.boxsysteminfo.theme.value = keys[(index + delta) % len(keys)]
        config.plugins.boxsysteminfo.theme.save()
        configfile.save()
        self.apply_theme()
        theme = THEMES.get(config.plugins.boxsysteminfo.theme.value, THEMES["midnight"])
        self["footer"].setText("◀ / ▶ %s    OK Aktualisieren    GELB Details    MENU Hilfe    EXIT Schließen" % theme["name"])

    def previous_theme(self):
        self._change_theme(-1)

    def next_theme(self):
        self._change_theme(1)

    def show_help(self):
        self.session.open(MessageBox,
            "Systeminfo für Enigma2.\n\nLinks/Rechts oder Grün: Theme wechseln\nGelb/Blau: Details öffnen\nIn Details: Hoch/Runter oder Gelb/Blau blättern\nOK: Werte aktualisieren; Exit: schließen\n\nHinweise ab: SoC 80 °C, Laufwerk 60 °C, Speicher 90 % belegt. Das sind Hinweisschwellen, keine Herstellergrenzwerte.\n\nSystemlast ist keine CPU-Prozentanzeige. Tunerbelegung erfasst Live-TV und bekannte Aufnahme-/Streaming-Frontends; unerkannte Nutzung kann bestehen. Werte werden nur beim Öffnen oder mit OK gelesen.",
            type=MessageBox.TYPE_INFO, timeout=8)


def _details_skin():
    widgets = []
    def label(name, x, y, width, height, font, opaque=False):
        widgets.append('<widget name="%s" position="%d,%d" size="%d,%d" font="Regular;%d" transparent="%d" zPosition="%d" />' %
                       (name, x, y, width, height, font, 0 if opaque else 1, 0 if opaque else 1))
    label("heading", 38, 25, 820, 48, 32)
    label("release", 926, 35, 150, 30, 20)
    label("subheading", 40, 79, 1030, 32, 21)
    label("panel", 36, 132, 1048, 416, 20, True)
    for index in range(12):
        label("label_%d" % index, 54, 150 + 32 * index, 266, 30, 20)
        label("value_%d" % index, 330, 150 + 32 * index, 736, 30, 21)
    label("note", 40, 553, 1040, 30, 17)
    label("footer", 40, 593, 1040, 32, 19)
    return '<screen name="BoxSystemInfoDetails" position="center,center" size="1120,650" title="Box Systeminfo">%s</screen>' % "".join(widgets)


class SystemDetails(Screen):
    skin = _details_skin()

    def __init__(self, session, owner):
        Screen.__init__(self, session)
        self.owner = owner
        self.page = 0
        for name in ("heading", "release", "subheading", "panel", "note", "footer"):
            self[name] = Label("")
        for index in range(12):
            self["label_%d" % index] = Label("")
            self["value_%d" % index] = Label("")
        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions"], {
            "cancel": self.close, "red": self.close, "ok": self.refresh,
            "up": self.previous_page, "down": self.next_page,
            "yellow": self.next_page, "blue": self.previous_page,
            "left": self.previous_theme, "right": self.next_theme,
            "green": self.next_theme, "menu": owner.show_help,
        }, -1)
        self.onLayoutFinish.append(self.render)
        self.render()

    def render(self):
        pages = self.owner.detail_pages()
        self.page %= len(pages)
        title, rows = pages[self.page]
        theme = THEMES.get(config.plugins.boxsysteminfo.theme.value, THEMES["midnight"])
        self["heading"].setText("Box Systeminfo · Details")
        self["release"].setText("Version " + VERSION)
        self["subheading"].setText(title)
        self["footer"].setText("▲ / ▼ Seite %d/%d    ◀ / ▶ %s    OK Aktualisieren    EXIT Zurück" % (self.page + 1, len(pages), theme["name"]))
        note = ""
        if title.startswith("Tuner"):
            note = "FBC umfasst virtuelle Frontends. Nicht erkannte Nutzung bedeutet nicht automatisch frei."
        elif title.startswith("Prozessor"):
            note = "Systemlast: Mittelwerte über 1, 5 und 15 Minuten; keine CPU-Auslastung in Prozent."
        elif title.startswith("Aufnahme"):
            note = "Aufnahmespeicher und SMART-Gerät können unterschiedlich sein, etwa bei Netzwerkaufnahmen."
        self["note"].setText(note)
        if self.instance is not None:
            self.owner._set_color(self, theme["bg"])
        self.owner._set_color(self["panel"], theme["panel"])
        for name in ("heading", "release", "subheading", "note", "footer"):
            self.owner._set_color(self[name], theme["bg"])
            self.owner._set_color(self[name], theme["text"] if name in ("heading", "subheading") else theme["muted"], True)
        for index in range(12):
            key, value = rows[index] if index < len(rows) else ("", "")
            self["label_%d" % index].setText(key)
            text = str(value)
            self["value_%d" % index].setText(text[:65] + "…" if len(text) > 66 else text)
            self.owner._set_color(self["label_%d" % index], theme["panel"])
            self.owner._set_color(self["value_%d" % index], theme["panel"])
            self.owner._set_color(self["label_%d" % index], theme["muted"], True)
            warning = (key == "Speicherbelegung" and self.owner._recording.get("percent", 0) >= STORAGE_WARNING
                       or key == "SMART-Gesamtstatus" and self.owner._drive_details.get("health_failed")
                       or key == "Laufwerkstemperatur" and _temperature_warning(self.owner._drive_value, DRIVE_WARNING)
                       or key == "Speicherstatus" and self.owner._recording.get("read_only"))
            self.owner._set_color(self["value_%d" % index], "#e46969" if warning else theme["text"], True)
        if self.instance is not None:
            self.instance.invalidate()

    def refresh(self):
        self.owner.refresh()
        self.render()

    def previous_page(self):
        self.page -= 1
        self.render()

    def next_page(self):
        self.page += 1
        self.render()

    def previous_theme(self):
        self.owner.previous_theme()
        self.render()

    def next_theme(self):
        self.owner.next_theme()
        self.render()


def main(session, **kwargs):
    session.open(BoxSystemInfo)


def Plugins(**kwargs):
    return [PluginDescriptor(name="Box Systeminfo", description="Receiver- und Image-Informationen", where=PluginDescriptor.WHERE_PLUGINMENU, icon="icon.png", fnc=main)]
