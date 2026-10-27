# Changelog

## 0.1.11 local test build (unreleased)

- Add ten-minute session-only curves for SoC and SSD temperatures and receive/send rates on the selected active network interface. Reuse an SSD reading only when it is no more than 60 seconds old; do not poll the drive just for history. Clear curves when the plugin closes.
- Allow three overview cards to use temperature, RAM, root storage, recording storage, or network. Keep defaults unchanged and swap selections when a chosen card is already in use. Save the choices.
- Add configurable visual warning thresholds: SoC 60–95 °C by 5 (default 80 °C), drive 40–70 °C by 5 (default 60 °C), and RAM/storage 75, 80, 85, 90, 95, or 98% (default 90%). These are advisories, not manufacturer limits.
- Expand RAM details with total, available, used, free, cache, buffers, and swap. Available memory includes reclaimable memory and is not additive with cache or buffers.
- Add a manual, numeric allowlist diagnostic export with the plugin version. Save it as JSON with mode 0600 in the runtime temporary directory. Exclude identifying/network data, local paths, logs, and credentials; do not upload it.
- Add a manual update check for published, non-prerelease ARMv7 packages in the official GitHub repository. The check reads metadata only and never downloads or installs assets.

Version 0.1.11 passes 95 tests and is installed on the receiver; Receiver GUI checks passed for history charts, RAM details, card and threshold settings, diagnostic export and the update check. English chart labels were also checked. It is not released. Version 0.1.9 remains the latest public IPK; publication approval for the user-tested 0.1.10 is still pending.

## 0.1.10 local test build (not released)

- Add configurable automatic refresh while the plugin is open, with Off, 2, 5, 10, and 30 second intervals and a 5 second default. Manual refresh remains available; automatic SMART queries run at most once per 60 seconds, while manual refresh forces a query.
- Add received and sent network rates in Mbit/s after two sysfs counter samples.
- Add live DVB signal quality in dB or relative percent, signal power (AGC), BER, and lock state when the active frontend supports them.
- Add allowlisted SMART wear and error counters. Remaining life is shown only for explicitly identified percentage fields; no estimate is derived from `Wear_Leveling_Count` or `Media_Wearout_Indicator`.
- Add GNU gettext English and German catalogs, automatic image-language selection with English fallback, and a menu language override.
- Add menu options for refresh interval and language, alongside help.

This local test build passes 67 tests and is installed on the receiver. The user confirmed that it works; publication approval is pending. Version 0.1.9 remains the latest public IPK; 0.1.10 has not been approved or released.

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
