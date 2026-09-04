# Enable the second USB serial port (data) used for song info + cover art.
import usb_cdc
usb_cdc.enable(console=True, data=True)
