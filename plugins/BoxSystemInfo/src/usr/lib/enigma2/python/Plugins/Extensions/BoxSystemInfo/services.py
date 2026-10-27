# -*- coding: utf-8 -*-
"""Privacy-safe diagnostic exports and a manual, metadata-only update check.

Diagnostic input schema (core sections are required; values may be None):
    {"cpu": {"cores": int, "load_1": number, "load_5": number,
             "load_15": number},
     "memory": {"total_bytes": int, "available_bytes": int},
     "root_storage": {"total_bytes": int, "free_bytes": int},
     "temperatures": {"soc_c": number, "drive_c": number},
     "recording_storage": {"total_bytes": int, "free_bytes": int}}  # optional

No identifying strings are accepted. Unknown keys at every level are rejected.
"""
from __future__ import print_function

import json
import math
import os
import re
import tempfile
import time

try:
    string_types = (basestring,)
except NameError:
    string_types = (str,)
try:
    integer_types = (int, long)
except NameError:
    integer_types = (int,)

VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")
GITHUB_API = "https://api.github.com/repos/Schrotty74/Enigma-Plugins/releases?per_page=100"
MAX_RESPONSE_BYTES = 512 * 1024
TIMEOUT_SECONDS = 8

# These are the only accepted diagnostic fields and their expected types.
_SCHEMA = {
    "cpu": {"cores": "int", "load_1": "number", "load_5": "number", "load_15": "number"},
    "memory": {"total_bytes": "int", "available_bytes": "int"},
    "root_storage": {"total_bytes": "int", "free_bytes": "int"},
    "temperatures": {"soc_c": "number", "drive_c": "number"},
    "recording_storage": {"total_bytes": "int", "free_bytes": "int"},
}


def _valid_number(value, kind):
    if value is None:
        return True
    if isinstance(value, bool) or not isinstance(value, integer_types + (float,)):
        return False
    if kind == "int" and not isinstance(value, integer_types):
        return False
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return False
    return value >= 0 if kind in ("int",) else True


def diagnostic_report(snapshot, plugin_version=None):
    """Return an allowlisted, JSON-serializable report; reject malformed input."""
    required = set(_SCHEMA) - set(("recording_storage",))
    if not isinstance(snapshot, dict) or not required.issubset(set(snapshot)) or set(snapshot) - set(_SCHEMA):
        raise ValueError("snapshot must contain the documented sections")
    report = {"schema_version": 1, "metrics": {}}
    if plugin_version is not None:
        if not isinstance(plugin_version, string_types) or _version_tuple(plugin_version) is None:
            raise ValueError("plugin_version must be a numeric dotted version")
        report["plugin_version"] = plugin_version
    for section, fields in _SCHEMA.items():
        if section not in snapshot:
            continue
        values = snapshot[section]
        if not isinstance(values, dict) or set(values) != set(fields):
            raise ValueError("invalid fields in %s" % section)
        clean = {}
        for key, kind in fields.items():
            value = values[key]
            if not _valid_number(value, kind):
                raise ValueError("invalid value for %s.%s" % (section, key))
            clean[key] = value
        report["metrics"][section] = clean
    # Ensure callers receive plain JSON data, with no custom objects.
    json.dumps(report, allow_nan=False)
    return report


def export_report(snapshot, directory=None, plugin_version=None):
    """Create an exclusive unique mode-0600 JSON report and return its path."""
    report = diagnostic_report(snapshot, plugin_version=plugin_version)
    directory = tempfile.gettempdir() if directory is None else directory
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    fd, path = tempfile.mkstemp(prefix="boxsysteminfo-diagnostic-%s-" % stamp,
                                suffix=".json", dir=directory)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as handle:
            fd = None
            json.dump(report, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        return path
    except Exception:
        if fd is not None:
            os.close(fd)
        try:
            os.unlink(path)
        except OSError:
            pass
        raise


def _version_tuple(value):
    if not isinstance(value, string_types) or not VERSION_RE.match(value):
        return None
    try:
        return tuple(int(part) for part in value.split("."))
    except (ValueError, OverflowError):
        return None


def _version_greater(candidate, current):
    # Numeric component comparison, padding missing trailing components with zero.
    size = max(len(candidate), len(current))
    return candidate + (0,) * (size - len(candidate)) > current + (0,) * (size - len(current))


def _published_versions(payload):
    if not isinstance(payload, list):
        raise ValueError("invalid release response")
    versions = []
    for release in payload:
        if not isinstance(release, dict) or release.get("draft") is not False or release.get("prerelease") is not False:
            continue
        tag = release.get("tag_name")
        match = re.match(r"^boxsysteminfo-v([0-9]+(?:\.[0-9]+)*)$", tag) if isinstance(tag, string_types) else None
        if not match:
            continue
        version = match.group(1)
        if _version_tuple(version) is None:
            continue
        expected = "enigma2-plugin-extensions-boxsysteminfo_%s_armv7ahf-neon.ipk" % version
        assets = release.get("assets")
        if not isinstance(assets, list) or not any(isinstance(asset, dict) and asset.get("name") == expected for asset in assets):
            continue
        versions.append(version)
    return versions


def check_update(current_version):
    """Query official published release metadata; never download or execute assets."""
    current = _version_tuple(current_version)
    if current is None:
        return {"status": "error", "version": None, "release_url": None}
    try:
        try:
            from urllib.request import Request, urlopen
        except ImportError:
            from urllib2 import Request, urlopen
        request = Request(GITHUB_API, headers={"User-Agent": "BoxSystemInfo-update-check", "Accept": "application/vnd.github+json"})
        response = urlopen(request, timeout=TIMEOUT_SECONDS)
        try:
            body = response.read(MAX_RESPONSE_BYTES + 1)
        finally:
            response.close()
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("release response too large")
        releases = _published_versions(json.loads(body.decode("utf-8")))
        eligible = [version for version in releases if _version_greater(_version_tuple(version), current)]
        if eligible:
            latest = max(eligible, key=lambda value: _version_tuple(value))
            return {"status": "newer", "version": latest,
                    "release_url": "https://github.com/Schrotty74/Enigma-Plugins/releases/tag/boxsysteminfo-v" + latest}
        return {"status": "current", "version": current_version, "release_url": None}
    except Exception:
        return {"status": "error", "version": current_version, "release_url": None}


def _main(argv):
    if len(argv) != 3 or argv[1] != "updates":
        result = {"status": "error", "version": None, "release_url": None}
    else:
        result = check_update(argv[2])
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    import sys
    _main(sys.argv)
