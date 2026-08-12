# hackpad3

3-key macropad from the [Hack Club Hackpad guide](https://hackpad.hackclub.com), based on the orpheuspad QMK config.

* Controller: Seeed XIAO RP2040
* Switches: direct-wired to physical pins 11 / 10 / 9 → GP3 / GP4 / GP2 (other leg to GND, no diodes)
* Keymap: Prev / Play-Pause / Next

## Build

Copy this folder to `qmk_firmware/keyboards/hackpad3`, then:

    qmk compile -kb hackpad3 -km default

## Flash

1. Hold the **BOOT** button on the XIAO while plugging in USB — it mounts as a drive called `RPI-RP2`.
2. Drag `hackpad3_default.uf2` onto the drive. It reboots as the macropad.

Re-enter the bootloader later via BOOT button, or bootmagic: hold the first key (GP3) while plugging in.
