# Changelog

## 0.1.11 — 2026-10-27

Version 0.1.10 was a development build and was not published separately. Its changes are included in this 0.1.11 release.

### Overview and controls

- Add three configurable overview cards. Each can show temperature, RAM, root storage, recording storage, or network. The defaults remain temperature, RAM, and root storage. Selecting a card already in use swaps the two selections. Choices are saved.
- Add automatic refresh options of Off, 2, 5, 10, or 30 seconds (default: 5 seconds), active only while the plugin is open. Manual refresh remains available. Automatic SMART queries run at most once every 60 seconds; a manual refresh forces a new query.
- Keep the general overview as the start screen, with detail pages for recording storage, SSD/SMART, CPU, RAM/swap, network, and tuners.

### History

- Add ten-minute session-only curves for SoC and SSD temperatures and receive/send rates on the active network interface. The history holds at most 300 points per series and 16 series in memory. It is cleared when the plugin closes and is never saved to disk.
- Record only fresh SSD readings received through normal query callbacks. Do not query the drive just to add a chart point. Missing readings remain gaps, with no reused samples or extrapolated values.

### Memory and warnings

- Add configurable visual warning thresholds: SoC 60–95 °C in 5-degree steps (default: 80 °C), drive 40–70 °C in 5-degree steps (default: 60 °C), and RAM/storage 75, 80, 85, 90, 95, or 98% (default: 90%). These thresholds are advisories, not manufacturer limits.
- Expand RAM details to show total, available, used, free, cache, buffers, and swap. Available memory includes reclaimable memory and should not be added to cache or buffers.

### SMART

- Add allowlisted SMART wear, reserve-space, write-volume, and error counters, including reallocated/pending/uncorrectable sectors, CRC transfer errors, program and erase failures, reported uncorrectable errors, end-to-end errors, reserve space, and supported host/NAND write totals. Show remaining life only for fields explicitly identified as percentages. Do not infer a percentage from `Wear_Leveling_Count` or `Media_Wearout_Indicator`.
- Keep SMART reads bounded and read-only. The bundled smartctl remains version 7.4; its original source archive and license files are included.

### Network and tuner

- Show receive and send rates in Mbit/s after two sysfs counter samples.
- Show active DVB frontend signal quality in dB or relative percent, signal power (AGC), BER, and lock state when supported. Read the active service without tuning or reserving a tuner.

### Language and refresh

- Add GNU gettext English and German catalogs. Select the image language when available, fall back to English, or choose a language from the menu.
- Add menu controls for refresh interval and language, alongside help. Manual SMART refresh remains available at any automatic refresh setting.

### Diagnostics, privacy, and update check

- Add a manual diagnostic export containing only the plugin version and strictly validated, allowlisted numeric CPU, memory, storage, and temperature fields. Unknown fields are rejected. The JSON file is written with mode 0600 to the runtime temporary directory. No identifiers, network details, local paths, logs, or credentials are included, and the plugin does not upload the report.
- Add a manual update check for published, non-prerelease ARMv7 packages in the official GitHub repository. It reads release metadata for up to 100 releases, with an 8-second request timeout and a 10-second process limit. It does not download or install assets.

### Validation and compatibility

- The 0.1.11 build passes 95 tests. Receiver GUI checks covered the history charts, RAM details, overview-card and threshold settings, diagnostic export, and update check; English chart labels were also checked. The user personally tested the build and confirmed that it works well.
- OpenATV and Python 2 have not been tested on a physical receiver. Compatibility with those environments is not confirmed.
- The smartctl 7.4 binary is unchanged. Plugin source, the original smartmontools source archive, and the included license files remain with the plugin.

## 0.1.9

- Detect a unique Enigma2-mounted recording partition when no recording path is configured. Leave the path unresolved when the mounted partitions are ambiguous.
- Label counts from running timer-list entries when the real-recording filter is unavailable.
- Publish the six feature additions from 0.1.8 below in the user-tested 0.1.9 package.

## 0.1.8

- Add detail pages for recording storage, SSD/SMART information, CPU, network, and tuners.
- Add warning colors for temperatures, storage use, SMART failures, and read-only storage.
- Keep FBC virtual frontends distinct from physical tuners and avoid reporting unobserved tuners as free.
- Read network interface state and negotiated speed from sysfs without exposing IP or MAC addresses.
- Display CPU clocks and system load averages rather than presenting load as a CPU percentage.
- Query recording storage in a separate process with a timeout.

## 0.1.7

- Add a transparent receiver icon for the plugin menu.

## 0.1.6

- Redraw the screen fully after theme changes and add text backgrounds to the cards.

## 0.1.5

- Bundle smartctl as a static ARMv7 binary with the original source and license files.
- Place section headings above the card backgrounds.

## 0.1.4

- Add cards for temperature, RAM, and root storage, with separate labels and values.

## 0.1.3

- Make SMART queries asynchronous with a timeout and status messages.
- Add PATH lookup and support for more temperature formats.
- Read image version and build information from additional sources.
- Use the Enigma2 version API and display the plugin version and image build date.

## 0.1.2

- Read drive temperature from SMART data.

## 0.1.1

- Prefer the Vu+ model identifier and add SoC and SSD temperatures.

## 0.1.0

- First test version with system information and themes.
