import time
import terminalio
import random
from adafruit_magtag.magtag import MagTag


magtag = MagTag(rotation=0)
magtag.peripherals.neopixel_disable = False

magtag.add_text(
    text_font='/fonts/helvB24.pcf',
    text_position=(68, 130),
    text_scale=6,
    text_anchor_point=(0.5, 0.5),
)

def get_random_letter_or_number():
    letter_number_set = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return random.choice(letter_number_set)

random_letter_or_number= get_random_letter_or_number()

magtag.set_text(random_letter_or_number)

magtag.exit_and_deep_sleep(10)
