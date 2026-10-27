# -*- coding: utf-8 -*-
"""Parse a small allowlist of useful, non-identifying smartctl attributes."""
from __future__ import print_function

import re

try:
    from .i18n import _
except (ImportError, ValueError):
    def _(text):
        return text


_ATA_FIELDS = {
    "reallocated_sector_ct": ("Remappte Sektoren", "errors"),
    "reallocated_event_count": ("Remappte Ereignisse", "errors"),
    "current_pending_sector": ("Ausstehende Sektoren", "errors"),
    "offline_uncorrectable": ("Nicht korrigierbare Sektoren", "errors"),
    "reported_uncorrect": ("Gemeldete unkorrigierbare Fehler", "errors"),
    "end-to-end_error": ("Ende-zu-Ende-Fehler", "errors"),
    "udma_crc_error_count": ("Übertragungsfehler", "errors"),
    "program_fail_count": ("Programmierfehler", "errors"),
    "erase_fail_count": ("Löschfehler", "errors"),
    "available_reserved_space": ("Verfügbare Reservesektoren", "percent"),
    "available_reservd_space": ("Verfügbare Reservesektoren", "percent"),
    "percent_lifetime_remain": ("Verbleibende Lebensdauer", "percent"),
    "host_writes_gib": ("Host-Schreibmenge", "gib"),
    "nand_gb_written_tlc": ("TLC-NAND-Schreibmenge", "counter"),
    "nand_gb_written_slc": ("SLC-NAND-Schreibmenge", "counter"),
}


def parse_smart_wear(output):
    """Return allowlisted SMART rows and an optional health warning.

    Unknown attribute names and all raw SMART output are deliberately ignored.
    """
    rows = []
    warning = None
    errors = []
    seen = set()
    raw_index = None
    for line in (output or "").splitlines():
        nvme = re.match(r"^\s*Percentage Used:\s*(\d+)\s*%?\s*$", line, re.I)
        if nvme:
            value = int(nvme.group(1))
            rows.append((_('Verschleiß (Percentage Used)'), _("%d%%") % value))
            if value >= 100:
                warning = _("Verschleißgrenze erreicht")
            continue
        media = re.match(r"^\s*Media and Data Integrity Errors:\s*(\d+)\s*$", line, re.I)
        if media:
            value = int(media.group(1))
            rows.append((_("Medienfehler"), str(value)))
            if value:
                errors.append(value)
            continue
        fields = line.split()
        if "ATTRIBUTE_NAME" in fields and "RAW_VALUE" in fields:
            raw_index = fields.index("RAW_VALUE")
            continue
        if len(fields) < 9 or not fields[0].isdigit():
            continue
        name, normalized = fields[1], fields[3]
        # smartctl normally includes WHEN_FAILED (raw starts at column 9),
        # while some builds omit it (raw starts at column 8).
        raw_start = raw_index if raw_index is not None else (9 if len(fields) >= 10 else 8)
        if len(fields) <= raw_start:
            continue
        raw = " ".join(fields[raw_start:])
        if not normalized.isdigit():
            continue
        name = name.lower()
        spec = _ATA_FIELDS.get(name)
        if spec is None or name in seen:
            continue
        seen.add(name)
        # Use numeric raw values for error counters. The remaining-life
        # attribute's normalized VALUE is explicitly a percentage scale.
        number_match = re.match(r"^\s*(\d+)(?:\s|$)", raw)
        if spec[1] not in ("percent",) and not number_match:
            continue
        value = int(normalized) if spec[1] == "percent" else int(number_match.group(1))
        label, kind = spec
        label = _(label)
        if kind == "percent":
            # These names explicitly describe remaining life; do not infer it
            # from normalized wear-leveling counts.
            if value <= 100:
                rows.append((label, _("%d%%") % value))
        else:
            rows.append((label, ("%d GiB" % value) if kind == "gib" else str(value)))
            if kind == "errors" and value:
                errors.append(value)
    if warning is None and errors:
        warning = _("SMART-Fehler erkannt")
    return {"wear_rows": rows, "wear_warning": warning}
