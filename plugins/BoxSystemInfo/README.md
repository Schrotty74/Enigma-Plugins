# Box Systeminfo 0.1.11 for Enigma2

[English](README.md) · [Deutsch](README.de.md) · [Changelog](CHANGELOG.md) · [Build instructions](BUILDING.md)

![Box Systeminfo](src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/icon.png)

Box Systeminfo displays receiver, storage, temperature and image information on an Enigma2 screen. Author: Schrotty74. It targets open Enigma2 images such as OpenPLi and OpenATV on ARMv7 receivers. Version 0.1.11 was tested successfully by the user and approved for publication.

[Download 0.1.11 and read the release notes](https://github.com/Schrotty74/Enigma-Plugins/releases/tag/boxsysteminfo-v0.1.11).

## Screenshots

[Open the gallery with all 12 screenshots](GALLERY.md): overview, detail pages, history charts and options.

## Features

- **Customizable overview:** three saved cards chosen from temperatures, RAM, root storage, recording storage and network. Selecting an existing card swaps its position.
- **Four themes:** Midnight, Ocean, Amber and Light, with the selection saved.
- **Receiver and image:** model, CPU, architecture, uptime, image name/version, build/date, Enigma2, kernel and Python versions.
- **SSD and SMART:** temperature, model, health, power-on hours, supported error counters, reserve space and write totals; remaining lifetime only for an unambiguous supported percentage attribute.
- **Recording storage:** capacity, used/free space, usage percentage, mount point and read-only status.
- **CPU:** online cores, current/maximum frequency and 1/5/15-minute load averages.
- **Network:** interface type, connection status, negotiated link speed and receive/send rates in Mbit/s.
- **Active DVB tuner:** signal quality in dB or relative percent, AGC, BER and lock, plus detected frontend use and recording counts.
- **History charts:** ten-minute temperature and network-rate curves held only in session RAM and cleared on closing.
- **Refresh options:** manual OK refresh or automatic Off/2/5/10/30-second intervals; default 5 seconds. Automatic SMART reads at most once per minute.

See the complete [feature overview](FEATURES.md) for all 16 features and additional technical details.

## Screen and controls

The main screen shows cards for temperatures, memory, and free root storage, followed by receiver and image details. The loaded plugin version appears in the upper right.

- Left/Right or Green: change theme. Midnight, Ocean, Amber, and Light are available, and the selection is saved.
- OK: refresh values.
- Exit or Red: close the plugin.
- Yellow or Blue: open details.
- In details, Up/Down or Yellow/Blue moves between storage/SSD, CPU, RAM/swap, network, and tuner pages. Exit returns to the main overview.
- Menu: set the refresh interval, language, overview cards and warning thresholds; open history charts, check for a released update, export a diagnostic report or open help. The interval options are Off, 2, 5, 10, and 30 seconds; the default is 5 seconds. The three overview cards can each use temperature, RAM, root storage, recording storage, or network. Defaults stay as shipped; choosing a card already in use swaps the selections. These choices are saved.

Automatic refresh runs only while the plugin is open. OK refreshes immediately. SMART data is queried at most once every 60 seconds during automatic refresh; pressing OK starts a new SMART query. Changing the theme does not start another query. There is no background service. The language follows the image setting when available and otherwise falls back to English. Menu options can override it.

## Installation

The IPK contains the plugin and a statically built `smartctl` for ARMv7. No separate smartmontools installation is needed. The plugin does not install `smartd`, add autostart entries, or change firmware or network settings.

```sh
opkg install /tmp/enigma2-plugin-extensions-boxsysteminfo_0.1.11_armv7ahf-neon.ipk
```

**Restart the Enigma2 user interface (GUI) after installation.** The new plugin version loads after the restart. Take any active recordings into account before restarting.

The image must accept the `armv7ahf-neon` package architecture. The bundled tool targets 32-bit ARMv7 Linux, not MIPS or a pure ARM64 system. Static linking avoids dependence on the image's C/C++ system-library versions, although image interfaces, drivers, and package architectures can still differ. Compatibility with every open image is not guaranteed. The Python source aims for Python 2/3 syntax; Python 2 has not been tested on a receiver.

## SSD temperature and SMART details

The plugin prefers its bundled smartctl 7.4 in `bin/`. The binary is 897,240 bytes. As a fallback, it searches `PATH` and common system directories. It reads data with `smartctl -n standby,3 -i -H -A`. It does not start SMART tests, enable SMART, or change drive settings. The standby option is intended to avoid waking a sleeping drive; support depends on the drive and its connection.

Where available, the details page also shows the drive model, overall SMART status, and power-on hours. Serial numbers are not displayed.

The SMART details include allowlisted wear and error counters when a drive supplies them: reallocated, pending, offline-uncorrectable, reported-uncorrectable, end-to-end, CRC, program-fail, and erase-fail counts. Available reserved space, explicitly named remaining-life percentages, host writes in GiB, and TLC/SLC NAND writes may also be shown. The plugin does not infer remaining life from `Wear_Leveling_Count` or `Media_Wearout_Indicator`. The WD attributes currently supported by the parser provide no safe remaining-life percentage.

Queries use `eConsoleAppContainer`, outside the GUI thread. An Enigma2 timer limits each attempt to three seconds, with at most four attempts per refresh. If smartctl explicitly requests a device type, the plugin makes one bounded SAT retry. Closing or refreshing cancels the active query. A matching hwmon sensor is used as a fallback.

The display distinguishes missing tools, standby, timeout, and missing temperature data. A missing value does not prove that a drive lacks a sensor. With multiple drives, the first available temperature is shown. The main card omits the device name.

## Additional details

- Recording storage: capacity, used and free space, percent used, and mount point. The configured recording path takes precedence. If none is configured, the plugin uses an Enigma2-mounted partition only when it finds exactly one candidate; it leaves the path unset when several candidates are ambiguous. An unmounted recording directory is not reported as a recording disk.
- Storage checks run in a separate Python process with a three-second timeout so a slow network filesystem cannot block the interface.
- CPU: online core count, current and maximum clock where available, and load averages over 1, 5, and 15 minutes. Load averages are not CPU-use percentages.
- Network: interface, type, connection state, negotiated link speed when the driver exports it, and received/sent rates in Mbit/s. Rates appear after two counter samples. No Internet query is made. IP and MAC addresses are not display fields.
- Tuners: configured frontends and detected active use. The active DVB service can also report signal quality in dB or a driver-relative percentage, relative signal power (AGC), BER, and lock state. Unsupported metrics remain unavailable. FBC tuners can expose virtual frontends. An unobserved frontend is not reported as free. The recording count uses a real-recording filter where available; the timer-list fallback is labelled as such.
- Warnings: adjustable SoC thresholds from 60 to 95 °C in 5-degree steps (default 80 °C), drive thresholds from 40 to 70 °C in 5-degree steps (default 60 °C), and RAM/storage thresholds of 75, 80, 85, 90, 95, or 98% (default 90%). SMART failures and read-only recording storage are also highlighted. These are visual advisories, not manufacturer limits.

The tuner view may not observe every active service, such as all streaming or picture-in-picture use. Its notes distinguish a frontend with no detected activity from one confirmed to be free.

## History, overview cards, and diagnostic tools

The optional history curves cover the last ten minutes of SoC and SSD temperature plus receive/send rates for the automatically chosen active network interface. SSD points are added only when a fresh drive query completes; a timer refresh does not duplicate a cached reading. The plugin does not poll the drive just to build a curve. History exists only for the current plugin session and is cleared when the plugin closes; it is not written to persistent storage. The Menu option **History charts** opens the chart view.

RAM details show total, available, used, free, cache, buffers, and swap. Available memory includes reclaimable memory; do not add it to cache and buffers.

**Export diagnostic report** is a manual Menu action. It writes a numeric allowlist and the plugin version to a JSON file in the runtime temporary directory with mode 0600. The report excludes IP and MAC addresses, serial numbers, hostnames, local paths, logs, and credentials. The plugin does not upload the file.

**Check for updates** is also manual from the Menu. It checks metadata for published, non-prerelease ARMv7 packages in the official GitHub repository. It does not download or install release assets. The network request runs outside the GUI thread and has a timeout.

## Image and Enigma2 versions

Detection optionally uses `Components.SystemInfo.BoxInfo` and `boxbranding`, then checks `/usr/lib/enigma.info`, `/etc/image-version`, `/etc/os-release`, and `/etc/issue` for a name fallback. Image version, build, and available build date are shown separately. Missing values remain `—`.

The Enigma2 version is read from `enigma.getEnigmaVersionString()` where available, with the About interface as a fallback. The plugin no longer uses `/etc/version` for this value.

References: [OpenPLi BoxInfo](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/python/Components/SystemInfo.py), [OpenPLi About](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/python/Components/About.py), [OpenWebif image detection](https://github.com/oe-alliance/OpenWebif/blob/main/plugin/controllers/models/info.py), [Enigma2 process handling](https://github.com/OpenPLi/enigma2/blob/scarthgap/lib/base/console.cpp).

## Build and tests

See [BUILDING.md](BUILDING.md) for the complete build procedure.

```sh
./build.sh
python3 -B -m unittest discover -s tests -v
```

The package build uses Python 3 and `tar`. The script reuses the bundled ARMv7 program, creates an opkg-compatible ar archive under `dist/`, and removes temporary build files. Tests cover temperature parsing, image fallbacks, storage mount selection, SMART fields, warning thresholds, process cancellation, and screen lifecycle with Enigma2 test doubles.

To rebuild smartctl, Zig 0.14.1, `make`, and the configure files in the included source archive are required:

```sh
ZIG="$(command -v zig)" ./tools/build-smartctl.sh
./build.sh
```

The source archive contains plugin code, tests, build scripts, the original smartmontools source, and license files. Source provenance, build parameters, and checksums are documented in `src/usr/share/doc/boxsysteminfo/smartmontools/HERKUNFT.md`. Source and license files are also included in the IPK.

## Compatibility and verification

Version 0.1.11 passes 95 automated tests. Receiver checks covered the overview, details, history charts, card selection, warning thresholds, German/English, diagnostic contents and file permissions, and the manual update check. The user then tested the installed package and approved publication.

Practical receiver testing used OpenPLi on a Vu+ Uno 4K SE. OpenATV and Python 2 remain untested on hardware; compatibility with every open image is not guaranteed. Timeout and cancellation tests use Enigma2 test doubles rather than deliberately blocking a receiver drive.

The current release is 0.1.11, tagged `boxsysteminfo-v0.1.11`. The detailed English [changelog](CHANGELOG.md) includes changes from the intermediate 0.1.10 development build. Earlier public releases remain available.

## Updates

The Menu provides an optional manual check for published releases. It reads release metadata from the official GitHub repository, filters for released non-prerelease ARMv7 packages, and never downloads or installs an asset. No automatic checks run.

## License

The plugin code is MIT-licensed; see `LICENSE`. smartctl is GPL version 2. Bundled static runtimes have their own license files in the documentation directory listed above.
