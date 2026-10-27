#!/usr/bin/env python3
"""Compile the plugin's singular UTF-8 PO catalogs without external tools."""
import ast
from pathlib import Path
import struct


def read_po(path):
    entries = {}
    msgid = msgstr = None
    field = None
    for line in path.read_text(encoding="utf-8").splitlines() + [""]:
        line = line.strip()
        if not line:
            if msgid is not None and msgstr is not None:
                if msgid in entries:
                    raise ValueError("Duplicate msgid in %s" % path)
                entries[msgid] = msgstr
            msgid = msgstr = field = None
        elif line.startswith("#"):
            continue
        elif line.startswith("msgid "):
            msgid, field = ast.literal_eval(line[6:]), "id"
        elif line.startswith("msgstr "):
            msgstr, field = ast.literal_eval(line[7:]), "str"
        elif line.startswith('"') and field:
            if field == "id":
                msgid += ast.literal_eval(line)
            else:
                msgstr += ast.literal_eval(line)
        else:
            raise ValueError("Unsupported PO syntax in %s" % path)
    return entries


def compile_po(path):
    entries = read_po(path)
    keys = sorted(entries)
    originals = [key.encode("utf-8") for key in keys]
    translated = [entries[key].encode("utf-8") for key in keys]
    count = len(keys)
    offset = 28 + 16 * count
    tables = []
    data = bytearray()
    for strings in (originals, translated):
        table = []
        for value in strings:
            table.append((len(value), offset + len(data)))
            data.extend(value + b"\0")
        tables.append(table)
    result = struct.pack("<7I", 0x950412de, 0, count, 28, 28 + 8 * count, 0, 0)
    result += b"".join(struct.pack("<2I", *entry) for table in tables for entry in table)
    path.with_suffix(".mo").write_bytes(result + data)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for path in sorted((root / "src").rglob("BoxSystemInfo.po")):
        compile_po(path)
