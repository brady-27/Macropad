#!/usr/bin/env python3
"""Companion script: pushes the currently playing Spotify track (title, artist,
cover art) to the Spotify Pad over USB serial.

Setup:
    pip install spotipy pyserial pillow requests

    Create an app at https://developer.spotify.com/dashboard, set redirect URI
    to http://127.0.0.1:8888/callback, then:
        export SPOTIPY_CLIENT_ID=...
        export SPOTIPY_CLIENT_SECRET=...
        export SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

    python spotify_display.py            # auto-detects the pad's serial port
    python spotify_display.py COM5       # or name the port explicitly
"""
import io
import sys
import time

import requests
import serial
import serial.tools.list_ports
import spotipy
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth

COVER = 160  # must match firmware


def find_port(arg_port=None):
    if arg_port:
        return arg_port
    ports = [p for p in serial.tools.list_ports.comports()
             if p.vid == 0x2E8A]  # Raspberry Pi USB VID (XIAO RP2040 CircuitPython)
    # CircuitPython exposes console first, data second — pick the last matching port
    if not ports:
        sys.exit("Spotify Pad not found — pass the serial port explicitly.")
    return sorted(ports, key=lambda p: p.device)[-1].device


def rgb565(img: Image.Image) -> bytes:
    img = img.convert("RGB").resize((COVER, COVER))
    out = bytearray(COVER * COVER * 2)
    i = 0
    for r, g, b in img.getdata():
        v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        out[i] = v >> 8
        out[i + 1] = v & 0xFF
        i += 2
    return bytes(out)


def main():
    port = find_port(sys.argv[1] if len(sys.argv) > 1 else None)
    ser = serial.Serial(port, 115200, timeout=1)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-currently-playing"))
    print(f"Connected to {port}. Polling Spotify...")

    last_track = None
    while True:
        try:
            cur = sp.current_user_playing_track()
            if cur and cur.get("item"):
                item = cur["item"]
                tid = item["id"]
                if tid != last_track:
                    last_track = tid
                    title = item["name"]
                    artist = ", ".join(a["name"] for a in item["artists"])
                    ser.write(f"TXT|{title}|{artist}\n".encode())
                    images = item["album"]["images"]
                    if images:
                        img = Image.open(io.BytesIO(requests.get(images[-1]["url"], timeout=10).content))
                        data = rgb565(img)
                        ser.write(f"IMG|{len(data)}\n".encode())
                        ser.write(data)
                    print(f"→ {title} — {artist}")
        except (serial.SerialException, OSError):
            print("Serial lost, retrying...")
            time.sleep(3)
            try:
                ser = serial.Serial(port, 115200, timeout=1)
            except OSError:
                pass
        except Exception as e:  # Spotify API hiccups
            print("warn:", e)
        time.sleep(3)


if __name__ == "__main__":
    main()
