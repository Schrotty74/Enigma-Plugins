# -*- coding: utf-8 -*-
"""Plugin-local gettext catalogs; follow the image language by default."""
from __future__ import print_function
import gettext
import os

_catalogs = {}


def selected_language():
    selected = "system"
    try:
        from Components.config import config
        selected = config.plugins.boxsysteminfo.language.value
    except (ImportError, AttributeError):
        pass
    if selected == "system":
        try:
            from Components.Language import language
            selected = language.getLanguage()
        except (ImportError, AttributeError):
            selected = "en"
    return "de" if selected.lower().startswith("de") else "en"


def _(text):
    if not text:
        return text
    # German source msgids retain compatibility with the existing probe output.
    # English is the fallback UI for all other image languages.
    language = selected_language()
    if language not in _catalogs:
        _catalogs[language] = gettext.translation(
            "BoxSystemInfo", os.path.join(os.path.dirname(__file__), "locale"),
            languages=[language], fallback=True)
    return _catalogs[language].gettext(text)
