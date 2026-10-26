#!/usr/bin/env python3
"""Inspect staged Git blobs and optional release archives without printing sensitive values."""
import hashlib
import io
import ipaddress
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import zipfile

PUBLIC_SOURCE_SHA256 = 'e9a61f641ff96ca95319edfb17948cd297d0cd3342736b2c49c99d4716fb993d'
PATTERNS = {
    'personal filesystem path': re.compile(rb'/(?:Users|home)/[A-Za-z0-9_.-]+(?:/|\b)|[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+'),
    'access token / private key': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,})\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'MAC address': re.compile(rb'(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])'),
}
IPV4 = re.compile(rb'(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9.])')
# RFC 1918 and IPv4 link-local ranges, represented numerically.
PRIVATE_NETWORKS = [ipaddress.ip_network(net) for net in ((0x0a000000, 8), (0xac100000, 12), (0xc0a80000, 16), (0xa9fe0000, 16))]
findings = []
verified_sources = 0


def inspect(data, label, depth=0):
    global verified_sources
    if depth > 8:
        findings.append((label, 'archive nesting limit'))
        return
    if hashlib.sha256(data).hexdigest() == PUBLIC_SOURCE_SHA256:
        # Exact public upstream bytes cannot contain local additions or session secrets.
        verified_sources += 1
        return
    for reason, pattern in PATTERNS.items():
        if pattern.search(data):
            findings.append((label, reason))
    for match in IPV4.finditer(data):
        try:
            addr = ipaddress.ip_address(match.group().decode('ascii'))
        except ValueError:
            continue
        if any(addr in net for net in PRIVATE_NETWORKS):
            findings.append((label, 'private IPv4 address'))
            break
    if data.startswith(b'!<arch>\n'):
        at = 8
        while at < len(data):
            header = data[at:at+60]
            try:
                size = int(header[48:58])
                name = header[:16].decode('ascii').strip().rstrip('/')
            except (ValueError, UnicodeDecodeError):
                findings.append((label, 'invalid ar member'))
                return
            inspect(data[at+60:at+60+size], label + ':' + name, depth+1)
            at += 60 + size + size % 2
    elif zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for member in archive.infolist():
                if not member.is_dir():
                    inspect(archive.read(member), label + ':' + member.filename, depth+1)
    elif data.startswith(b'\x1f\x8b') or label.endswith(('.tar', '.tar.gz', '.tgz')):
        try:
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                for member in archive:
                    member_label = label + ':' + member.name
                    if member.uid != 0 or member.gid != 0 or member.uname not in ('', 'root') or member.gname not in ('', 'root'):
                        findings.append((member_label, 'non-neutral archive owner metadata'))
                    if member.pax_headers:
                        findings.append((member_label, 'extended archive metadata requires review'))
                    if member.isfile():
                        inspect(archive.extractfile(member).read(), member_label, depth+1)
        except tarfile.TarError:
            findings.append((label, 'cannot inspect compressed archive'))


def main():
    root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMRT', '-z'], cwd=root).split(b'\0')
    count = 0
    for entry in staged:
        if not entry:
            continue
        name = entry.decode('utf-8')
        data = subprocess.check_output(['git', 'show', ':' + name], cwd=root)
        inspect(data, name)
        count += 1
    for arg in sys.argv[1:]:
        path = Path(arg)
        inspect(path.read_bytes(), path.name)
        count += 1
    if not count:
        print('No staged files or release artifacts selected. Stage the exact upload first.')
        return 2
    if findings:
        for label, reason in sorted(set(findings)):
            print('%s: %s' % (label, reason))
        print('STOP: review findings before upload. This audit never prints matched values.')
        return 1
    print('Upload audit passed: %d staged files/artifacts; %d exact public upstream source archives verified.' % (count, verified_sources))
    print('Also manually review selected files for contextual personal data and publication approval.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
