# Box Systeminfo 0.1.9 for Enigma2

[English](README.md) · [Deutsch](README.de.md) · [Changelog](CHANGELOG.md) · [Build instructions](BUILDING.md)

![Box Systeminfo](src/usr/lib/enigma2/python/Plugins/Extensions/BoxSystemInfo/icon.png)

Box Systeminfo displays receiver, storage, temperature, and image information on an Enigma2 screen. The author is Schrotty74. It targets open Enigma2 images such as OpenPLi and OpenATV on ARMv7 receivers. Version 0.1.9 was tested on the user's receiver; the user confirmed that the data is now displayed and approved publication of the IPK.

## Screen and controls

The main screen shows cards for temperatures, memory, and free root storage, followed by receiver and image details. The loaded plugin version appears in the upper right.

- Left/Right or Green: change theme. Midnight, Ocean, Amber, and Light are available, and the selection is saved.
- OK: refresh values.
- Exit or Red: close the plugin.
- Yellow or Blue: open details.
- In details, Up/Down or Yellow/Blue moves between storage/SSD, CPU, network, and tuner pages. Exit returns to the main overview.
- Menu: open help.

The plugin reads values when opened and when refreshed with OK. Changing the theme does not start another query. There is no background service.

## Installation

The IPK contains the plugin and a statically built `smartctl` for ARMv7. No separate smartmontools installation is needed. The plugin does not install `smartd`, add autostart entries, or change firmware or network settings.

```sh
opkg install /tmp/enigma2-plugin-extensions-boxsysteminfo_0.1.9_armv7ahf-neon.ipk
```

**Restart the Enigma2 user interface (GUI) after installation.** The new plugin version loads after the restart. Take any active recordings into account before restarting.

The image must accept the `armv7ahf-neon` package architecture. The bundled tool targets 32-bit ARMv7 Linux, not MIPS or a pure ARM64 system. Static linking avoids dependence on the image's C/C++ system-library versions, although image interfaces, drivers, and package architectures can still differ. Compatibility with every open image is not guaranteed. The Python source aims for Python 2/3 syntax; Python 2 has not been tested on a receiver.

## SSD temperature and SMART details

The plugin prefers its bundled smartctl 7.4 in `bin/`. The binary is 897,240 bytes. As a fallback, it searches `PATH` and common system directories. It reads data with `smartctl -n standby,3 -i -H -A`. It does not start SMART tests, enable SMART, or change drive settings. The standby option is intended to avoid waking a sleeping drive; support depends on the drive and its connection.

Where available, the details page also shows the drive model, overall SMART status, and power-on hours. Serial numbers are not displayed.

Queries use `eConsoleAppContainer`, outside the GUI thread. An Enigma2 timer limits each attempt to three seconds, with at most four attempts per refresh. If smartctl explicitly requests a device type, the plugin makes one bounded SAT retry. Closing or refreshing cancels the active query. A matching hwmon sensor is used as a fallback.

The display distinguishes missing tools, standby, timeout, and missing temperature data. A missing value does not prove that a drive lacks a sensor. With multiple drives, the first available temperature is shown. The main card omits the device name.

## Additional details

- Recording storage: capacity, used and free space, percent used, and mount point. The configured recording path takes precedence. If none is configured, the plugin uses an Enigma2-mounted partition only when it finds exactly one candidate; it leaves the path unset when several candidates are ambiguous. An unmounted recording directory is not reported as a recording disk.
- Storage checks run in a separate Python process with a three-second timeout so a slow network filesystem cannot block the interface.
- CPU: online core count, current and maximum clock where available, and load averages over 1, 5, and 15 minutes. Load averages are not CPU-use percentages.
- Network: interface, type, connection state, and negotiated link speed when the driver exports it. No Internet query is made. IP and MAC addresses are not display fields.
- Tuners: configured frontends and detected active use. FBC tuners can expose virtual frontends. An unobserved frontend is not reported as free. The recording count uses a real-recording filter where available; the timer-list fallback is labelled as such.
- Warnings: SoC temperature from 80 °C, drive temperature from 60 °C, and storage use from 90%. SMART failures and read-only recording storage are also highlighted. These are notification thresholds, not manufacturer limits.

The tuner view may not observe every active service, such as all streaming or picture-in-picture use. Its notes distinguish a frontend with no detected activity from one confirmed to be free.

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

The 0.1.9 package has been built and the 48 regression tests pass. The user tested it on a receiver and confirmed that the data is displayed. OpenPLi and OpenATV are target images; OpenATV, other receivers, and Python 2 have not been tested on hardware. The plugin makes no universal compatibility claim. Tests use doubles for timeouts and process failures rather than deliberately blocking a receiver drive.

The current release is 0.1.9. See the English [changelog](CHANGELOG.md) for earlier changes. The source tag is `boxsysteminfo-v0.1.9`.

## Updates

There is no fixed release schedule or automatic update source. New packages are built when needed and may include a newer tested smartctl version. The plugin does not download programs. The bundled tool is part of the plugin package and can therefore be updated with it.

## License

The plugin code is MIT-licensed; see `LICENSE`. smartctl is GPL version 2. Bundled static runtimes have their own license files in the documentation directory listed above.
