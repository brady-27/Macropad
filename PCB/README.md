# Spotify Pad

A media macropad: 3 hotswap MX keys (⏮ ⏯ ⏭), an EC11 rotary encoder for volume
(push = mute), and a 1.54" ST7789 240×240 color display showing the current
song, artist, and album cover. Brain: Seeed Studio XIAO RP2040 (USB-C).

Board: 80 × 92 mm, 2 layers. Passes KiCad DRC with 0 errors, all nets routed,
ground pours on both sides. Schematic and PCB netlists verified identical.

## Files

- `spotify-pad.kicad_pro / .kicad_sch / .kicad_pcb` — full KiCad 7 project
  (opens fine in KiCad 8/9 too, they read v7 files)
- `footprints/SpotifyPad.pretty/` — project-local footprints (self-contained,
  including the XIAO RP2040 DIP footprint and the Kailh hotswap socket)
- `gerbers/` — ready-to-order gerbers + Excellon drill files (zip the folder
  and upload to JLCPCB / PCBWay as-is)
- `BOM.csv` — parts list (~$15 in parts + switches/caps)
- `firmware/` — CircuitPython `boot.py` + `code.py` for the XIAO
- `host/spotify_display.py` — desktop script that feeds song info + cover art
  to the display via USB serial (Spotify Web API)

## How it works

The three keys and the encoder send **standard USB media keys** — they work
immediately with Spotify, YouTube, anything, on any OS, no software needed.

The display can't pull album art on its own (the XIAO has no WiFi), so the
little `spotify_display.py` script runs on your computer, polls the Spotify
API, and streams the title/artist/cover over the same USB cable.

## Wiring (already routed on the PCB)

| XIAO pin | Signal | Goes to |
|---|---|---|
| D0 | SW_BACK | Key 1 (⏮) |
| D1 | SW_PLAY | Key 2 (⏯) |
| D2 | SW_NEXT | Key 3 (⏭) |
| D3 | ENC_SW | Encoder push |
| D4 | ENC_A | Encoder channel (east pad) |
| D5 | ENC_B | Encoder channel (west pad) |
| D6 | LCD_RST | Display RES |
| D7 | LCD_CS | Display CS |
| D8 (SCK) | LCD_SCK | Display SCL |
| D9 | LCD_DC | Display DC |
| D10 (MOSI) | LCD_MOSI | Display SDA |
| 3V3 | +3V3 | Display VCC, R1→BLK, C1 |

All switches go to ground; firmware uses internal pull-ups. R1 (0Ω) ties the
display backlight to 3V3 permanently — leave it off and bodge BLK to a spare
pin if you ever want PWM dimming.

## Build notes

1. **Hotswap sockets go on the BACK of the board** (the side without
   silkscreen labels). Switches click in from the front.
2. The XIAO solders on the front at the top-left, USB-C facing the top edge.
   Use the castellated edge pads flush, or 7-pin headers.
3. The display plugs into the 1×8 socket, module resting over the silkscreen
   outline. **Check your module's pin order** against the silk
   (BLK CS DC RES SDA SCL VCC GND, left→right) — most 1.54"/1.3" ST7789
   modules match, a few vendors swap pins.
4. Encoder: any EC11 with switch; 20mm shaft fits standard knobs.

## Firmware

1. Hold BOOT on the XIAO while plugging in → drag-drop CircuitPython UF2
   ([circuitpython.org/board/seeeduino_xiao_rp2040](https://circuitpython.org/board/seeeduino_xiao_rp2040/))
2. Copy `firmware/boot.py` and `firmware/code.py` to the CIRCUITPY drive
3. Copy `adafruit_hid`, `adafruit_st7789`, `adafruit_display_text` from the
   Adafruit CircuitPython bundle into `CIRCUITPY/lib/`
4. For the display feed: `pip install spotipy pyserial pillow requests`,
   create a (free) Spotify developer app, export the credentials, run
   `python host/spotify_display.py`

## Ordering the PCB

Upload a zip of `gerbers/` to JLCPCB: 2 layers, 1.6mm, any color (it's a
Spotify pad — green solder mask, obviously). Default options are fine.
