# -*- coding: utf-8 -*-
"""Session-only temperature and traffic charts using Enigma2's canvas."""
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.CanvasSource import CanvasSource

from .i18n import _
from .metrics import graph_segments


class HistoryScreen(Screen):
    skin = '''<screen name="BoxSystemInfoHistory" position="center,center" size="1120,650" title="Box Systeminfo">
        <widget name="heading" position="40,26" size="870,45" font="Regular;32" transparent="1" />
        <widget name="release" position="930,35" size="150,30" font="Regular;20" transparent="1" />
        <widget name="temperature_label" position="40,92" size="1040,32" font="Regular;21" transparent="1" />
        <widget source="temperature" render="Canvas" position="60,136" size="1000,130" />
        <widget name="temperature_legend" position="60,273" size="1000,30" font="Regular;19" transparent="1" />
        <widget name="network_label" position="40,323" size="1040,32" font="Regular;21" transparent="1" />
        <widget source="network" render="Canvas" position="60,367" size="1000,130" />
        <widget name="network_legend" position="60,504" size="1000,30" font="Regular;19" transparent="1" />
        <widget name="note" position="40,550" size="1040,28" font="Regular;17" transparent="1" />
        <widget name="footer" position="40,593" size="1040,32" font="Regular;19" transparent="1" />
    </screen>'''

    def __init__(self, session, owner):
        Screen.__init__(self, session)
        self.owner = owner
        for key in ("heading", "release", "temperature_label", "temperature_legend",
                    "network_label", "network_legend", "note", "footer"):
            self[key] = Label("")
        self["temperature"] = CanvasSource()
        self["network"] = CanvasSource()
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"], {
            "cancel": self.close, "red": self.close, "ok": self.refresh,
            "green": owner.next_theme, "menu": owner.show_menu,
        }, -1)
        self.onLayoutFinish.append(self.render)
        self.render()

    def _draw(self, key, series, maximum):
        theme = self.owner.current_theme()
        color = lambda name: int(theme[name].lstrip("#"), 16)
        canvas = self[key]
        canvas.clear()
        canvas.fill(0, 0, 1000, 130, color("panel"))
        for y in (0, 64, 129):
            canvas.line(0, y, 999, y, color("muted"))
        for points, line_color in series:
            for segment in graph_segments(points, 999, 129, minimum=0,
                                          maximum=maximum, now=self.owner._history.clock()):
                for first, second in zip(segment, segment[1:]):
                    canvas.line(int(first[0]), int(first[1]), int(second[0]), int(second[1]), line_color)
                if segment:
                    x, y = segment[-1]
                    canvas.fill(max(0, min(996, int(x) - 1)), max(0, min(126, int(y) - 1)), 3, 3, line_color)
        canvas.flush()

    def render(self):
        theme = self.owner.current_theme()
        history = self.owner._history
        soc, drive = history.points("soc"), history.points("drive")
        interface, receive, send = self.owner._network_current
        rx, tx = history.points("rx:" + interface), history.points("tx:" + interface)
        temperatures = [v for points in (soc, drive) for stamp, v in points if v is not None]
        rates = [v for points in (rx, tx) for stamp, v in points if v is not None]
        temp_max = max(100.0, max(temperatures or [0]) * 1.1)
        rate_max = max(1.0, max(rates or [0]) * 1.1)
        accent = int(theme["accent"].lstrip("#"), 16)
        ssd_color = 0x47a8e8 if theme["name"] == "Amber" else 0xffbd59
        ssd_name = _("Blau") if theme["name"] == "Amber" else _("Gelb")
        self._draw("temperature", ((soc, accent), (drive, ssd_color)), temp_max)
        self._draw("network", ((rx, accent), (tx, 0x47a8e8)), rate_max)
        self["heading"].setText(_("Verlauf der letzten 10 Minuten"))
        self["release"].setText("Version " + self.owner.version)
        self["temperature_label"].setText(_("Temperaturen · Skala 0–%.0f °C") % temp_max)
        self["temperature_legend"].setText(_("Akzent: SoC %s    %s: SSD %s    −10 Min. → Jetzt") %
                                          (self.owner._soc_value, ssd_name, self.owner._drive_value.split(" (", 1)[0]))
        self["network_label"].setText(_("Netzwerk %s · Skala 0–%.2f Mbit/s") % (interface, rate_max))
        self["network_legend"].setText(_("Akzent: Empfang %s    Blau: Versand %s    −10 Min. → Jetzt") %
                                      (self.owner.format_rate(receive), self.owner.format_rate(send)))
        self["note"].setText(_("Nur diese Sitzung; Messlücken bleiben offen. SSD-Werte werden seltener gelesen."))
        self["footer"].setText(_("OK Aktualisieren    GRÜN Theme    MENU Optionen    EXIT Zurück"))
        if self.instance is not None:
            self.owner._set_color(self, theme["bg"])
        for key in ("heading", "release", "temperature_label", "temperature_legend",
                    "network_label", "network_legend", "note", "footer"):
            self.owner._set_color(self[key], theme["bg"])
            self.owner._set_color(self[key], theme["muted"] if key in ("note", "footer", "release") else theme["text"], True)

    def refresh(self):
        self.owner.refresh()
