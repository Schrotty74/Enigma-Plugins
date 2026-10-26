# Changelog

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
