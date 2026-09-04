# Spotify Pad — CircuitPython firmware for Seeed XIAO RP2040
#
# Keys send USB media keys (work with Spotify or any player, no host app needed).
# The display listens on USB serial for song info + cover art pushed by the
# companion script host/spotify_display.py running on your computer.
#
# Setup:
#   1. Flash CircuitPython for XIAO RP2040 (circuitpython.org/board/seeeduino_xiao_rp2040)
#   2. Copy this file to CIRCUITPY/code.py
#   3. Copy adafruit_hid + adafruit_st7789 + adafruit_display_text libs to CIRCUITPY/lib
#
import time
import board
import busio
import digitalio
import rotaryio
import displayio
import usb_cdc
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

try:
    from fourwire import FourWire          # CircuitPython 9+
except ImportError:
    from displayio import FourWire         # CircuitPython 8

from adafruit_st7789 import ST7789
from adafruit_display_text import label as text_label
import terminalio

# ---------------- pins (match PCB) ----------------
PIN_SW_BACK = board.D0
PIN_SW_PLAY = board.D1
PIN_SW_NEXT = board.D2
PIN_ENC_SW = board.D3
PIN_ENC_EAST = board.D4    # encoder channel A (east pad)
PIN_ENC_WEST = board.D5    # encoder channel B (west pad)
PIN_LCD_RST = board.D6
PIN_LCD_CS = board.D7
PIN_LCD_SCK = board.D8
PIN_LCD_DC = board.D9
PIN_LCD_MOSI = board.D10

# ---------------- display ----------------
displayio.release_displays()
spi = busio.SPI(clock=PIN_LCD_SCK, MOSI=PIN_LCD_MOSI)
bus = FourWire(spi, command=PIN_LCD_DC, chip_select=PIN_LCD_CS, reset=PIN_LCD_RST)
display = ST7789(bus, width=240, height=240, rowstart=80, rotation=0)

root = displayio.Group()
display.root_group = root

cover_bitmap = displayio.Bitmap(160, 160, 65536)
cover_shader = displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565)
cover_tile = displayio.TileGrid(cover_bitmap, pixel_shader=cover_shader, x=40, y=8)
root.append(cover_tile)

song_lbl = text_label.Label(terminalio.FONT, text="Spotify Pad", color=0xFFFFFF, x=8, y=185, scale=2)
artist_lbl = text_label.Label(terminalio.FONT, text="waiting for host...", color=0x1DB954, x=8, y=215, scale=1)
root.append(song_lbl)
root.append(artist_lbl)

# ---------------- inputs ----------------
cc = ConsumerControl(usb_hid.devices)

def make_button(pin):
    b = digitalio.DigitalInOut(pin)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    return b

btn_back = make_button(PIN_SW_BACK)
btn_play = make_button(PIN_SW_PLAY)
btn_next = make_button(PIN_SW_NEXT)
btn_mute = make_button(PIN_ENC_SW)
encoder = rotaryio.IncrementalEncoder(PIN_ENC_EAST, PIN_ENC_WEST)

last_pos = encoder.position
prev = {"back": True, "play": True, "next": True, "mute": True}

# ---------------- serial protocol ----------------
# Host sends lines over the data serial port:
#   TXT|<song title>|<artist>\n
#   IMG|<len>\n  followed by <len> raw RGB565 big-endian bytes (160x160)
ser = usb_cdc.data

def poll_serial():
    if ser is None or ser.in_waiting == 0:
        return
    line = ser.readline()
    if not line:
        return
    try:
        line = line.decode().strip()
    except UnicodeError:
        return
    if line.startswith("TXT|"):
        parts = line.split("|")
        if len(parts) >= 3:
            song_lbl.text = parts[1][:18]
            artist_lbl.text = parts[2][:38]
    elif line.startswith("IMG|"):
        try:
            n = int(line.split("|")[1])
        except (IndexError, ValueError):
            return
        buf = bytearray(n)
        mv = memoryview(buf)
        got = 0
        deadline = time.monotonic() + 5
        while got < n and time.monotonic() < deadline:
            if ser.in_waiting:
                got += ser.readinto(mv[got:])
        if got == n:
            idx = 0
            for y in range(160):
                for x in range(160):
                    cover_bitmap[x, y] = (buf[idx] << 8) | buf[idx + 1]
                    idx += 2

while True:
    # buttons (active low)
    for name, btn, code in (
        ("back", btn_back, ConsumerControlCode.SCAN_PREVIOUS_TRACK),
        ("play", btn_play, ConsumerControlCode.PLAY_PAUSE),
        ("next", btn_next, ConsumerControlCode.SCAN_NEXT_TRACK),
        ("mute", btn_mute, ConsumerControlCode.MUTE),
    ):
        pressed = not btn.value
        if pressed and prev[name]:
            cc.send(code)
        prev[name] = pressed

    # encoder -> volume
    pos = encoder.position
    while pos > last_pos:
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        last_pos += 1
    while pos < last_pos:
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        last_pos -= 1

    poll_serial()
    time.sleep(0.005)
