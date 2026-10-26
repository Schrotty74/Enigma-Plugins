# -*- coding: utf-8 -*-
"""Bounded worker entry point for potentially slow recording filesystem reads."""
from __future__ import print_function
import json
import os
import re
import sys


def _unescape_mount(value):
    return re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), value)


def storage_info(path):
    result = {"path": path, "status": "Nicht verfügbar"}
    try:
        path = os.path.realpath(path)
        entries = []
        with open('/proc/mounts', 'r') as handle:
            for line in handle:
                fields = line.split()
                if len(fields) >= 4:
                    device, mount, filesystem, options = fields[:4]
                    mount = _unescape_mount(mount).rstrip('/') or '/'
                    if path == mount or path.startswith(mount.rstrip('/') + '/'):
                        entries.append((len(mount), _unescape_mount(device), mount, filesystem, options))
        if not entries:
            return result
        _, device, mount, filesystem, options = max(entries)
        result.update(mount=mount, filesystem=filesystem, read_only='ro' in options.split(','))
        # Never mistake an unmounted recording directory for a recording disk.
        if mount == '/':
            result['status'] = 'Kein eigener Aufnahmespeicher eingehängt'
            return result
        if device.startswith('/dev/'):
            result['device'] = device
        else:
            result['device'] = 'Netzwerk / virtuell'
        target = path if os.path.isdir(path) else mount
        stats = os.statvfs(target)
        total = stats.f_blocks * stats.f_frsize
        free = stats.f_bavail * stats.f_frsize
        used = (stats.f_blocks - stats.f_bfree) * stats.f_frsize
        result.update(total=total, free=free, used=used,
                      percent=int(100.0 * used / (used + free)) if used + free else 0,
                      status='Nur lesbar' if result['read_only'] else 'Verfügbar')
    except (IOError, OSError, ValueError):
        pass
    return result


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) == 2 else ''
    result = storage_info(path) if os.path.isabs(path) else {'status': 'Kein Aufnahmepfad ermittelt'}
    print(json.dumps(result, ensure_ascii=True))
