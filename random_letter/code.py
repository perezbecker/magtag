import time
import terminalio
import random
from adafruit_magtag.magtag import MagTag


magtag = MagTag()
magtag.peripherals.neopixel_disable = False

magtag.add_text(
    text_font='/fonts/helvB24.pcf',
    text_position=(150,50),
    text_scale=5,
    text_anchor_point=(0.5, 0.5),
)

def get_random_letter_or_number():
    letter_number_set = ['0','1','2','3','4','5','6','7','8','9','A a','B b','C c','D d','E e','F f','G g','H h','I i','J j','K k','L l','M m','N n','O o','P p','Q q','R r','S s','T t','U u','V v','W w','X x','Y y','Z z']
    return random.choice(letter_number_set)

random_letter_or_number= get_random_letter_or_number()

magtag.set_text(random_letter_or_number)

magtag.exit_and_deep_sleep(10)
