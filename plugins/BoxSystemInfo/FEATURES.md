# Box Systeminfo — complete feature overview

[English](FEATURES.md) · [Deutsch](FEATURES.de.md) · [Back to README](README.md)

Features of the published Box Systeminfo 0.1.11 release. Hardware-dependent values are only available if the receiver, drive, tuner or image provides them.

## Features

- **Customizable overview:** three saved cards chosen from temperatures, RAM, root storage, recording storage and network. Selecting an existing card swaps its position.
- **Four themes:** Midnight, Ocean, Amber and Light, with the selection saved.
- **Receiver and image:** model, CPU, architecture, uptime, image name/version, build/date, Enigma2, kernel and Python versions.
- **SSD and SMART:** temperature, model, health, power-on hours, supported error counters, reserve space and write totals; remaining lifetime only for an unambiguous supported percentage attribute.
- **Recording storage:** capacity, used/free space, usage percentage, mount point and read-only status.
- **CPU:** online cores, current/maximum frequency and 1/5/15-minute load averages.
- **RAM and swap:** total, available, used and unused RAM, adjusted cache, buffers, and total/used/free swap.
- **Network:** interface type, connection status, negotiated link speed and receive/send rates in Mbit/s.
- **Active DVB tuner:** signal quality in dB or relative percent, AGC, BER and lock, plus detected frontend use and recording counts.
- **History charts:** ten-minute temperature and network-rate curves held only in session RAM and cleared on closing.
- **Refresh options:** manual OK refresh or automatic Off/2/5/10/30-second intervals; default 5 seconds. Automatic SMART reads at most once per minute.
- **Warning settings:** saved SoC/drive temperature and RAM/storage usage thresholds, plus SMART and read-only storage warnings.
- **German and English:** image-language selection with English fallback or a direct Menu override.
- **Diagnostic export:** manual JSON report with only the plugin version and approved numeric fields, mode 0600 and no upload.
- **Update notification:** manual search for newer published ARMv7 plugin packages; no automatic package download or installation.
- **Complete ARMv7 package:** static smartctl 7.4, original smartmontools sources, licenses and build scripts included.

For controls, installation, SMART behaviour, compatibility, diagnostics and build instructions, see the [project README](README.md).
