#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WORK=$(mktemp -d "$ROOT/.build.XXXXXX")
trap 'rm -rf "$WORK"' EXIT HUP INT TERM
DIST="$ROOT/dist"
VERSION="0.1.9"
mkdir -p "$DIST"
python3 - "$ROOT" "$WORK" "$DIST" "$VERSION" <<'PY'
import gzip
import os
import sys
import tarfile
root, work, dist, version = sys.argv[1:]
control_path = os.path.join(root, "src", "CONTROL", "control")
with open(control_path) as handle:
    control = dict(line.rstrip().split(": ", 1) for line in handle if ": " in line)
assert control["Version"] == version, "Build/control version mismatch"
out = os.path.join(dist, "%s_%s_%s.ipk" % (control["Package"], version, control["Architecture"]))

def neutral_metadata(info):
    if any(part == "__pycache__" or part == ".DS_Store" or part.endswith((".pyc", ".pyo")) for part in info.name.split("/")):
        return None
    info.uid = info.gid = 0
    info.uname = info.gname = "root"
    info.mtime = 0
    info.pax_headers = {}
    return info

for name, source, arcname in (("control", control_path, "./control"), ("data", os.path.join(root, "src", "usr"), "./usr")):
    with open(os.path.join(work, name + ".tar.gz"), "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                archive.add(source, arcname=arcname, filter=neutral_metadata)
with open(os.path.join(work, "debian-binary"), "wb") as handle:
    handle.write(b"2.0\n")
with open(out, "wb") as archive:
    archive.write(b"!<arch>\n")
    for name in ("debian-binary", "control.tar.gz", "data.tar.gz"):
        with open(os.path.join(work, name), "rb") as member:
            data = member.read()
        header = "%-16s%-12d%-6d%-6d%-8s%-10d`\n" % (name + "/", 0, 0, 0, "100644", len(data))
        archive.write(header.encode("ascii"))
        archive.write(data)
        if len(data) % 2:
            archive.write(b"\n")
print("Created %s" % os.path.relpath(out, root))
PY
