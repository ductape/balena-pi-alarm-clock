#!/usr/bin/env python3

import time
from datetime import datetime
from colorsys import hsv_to_rgb
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from ST7789 import ST7789

import RPi.GPIO as GPIO

import simpleaudio as sa

print("""rainbow.py - Display a rainbow on the Pirate Audio LCD

This example should demonstrate how to:
1. set up the Pirate Audio LCD,
2. create a PIL image to use as a buffer,
3. draw something into that image,
4. and display it on the display

You should see the display change colour.

Press Ctrl+C to exit!

""")

SPI_SPEED_MHZ = 80

image = Image.new("RGB", (240, 240), (0, 0, 0))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)


st7789 = ST7789(
    rotation=90,  # Needed to display the right way up on Pirate Audio
    port=0,       # SPI port
    cs=1,         # SPI port Chip-select channel
    dc=9,         # BCM pin used for data/command
    backlight=13,
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)

# Load the sounds
wav_obj = sa.WaveObject.from_wave_file('applause-1.wav')

# The buttons on Pirate Audio are connected to pins 5, 6, 16 and 24
# Boards prior to 23 January 2020 used 5, 6, 16 and 20
# try changing 24 to 20 if your Y button doesn't work.
BUTTONS = [5, 6, 16, 20]

# These correspond to buttons A, B, X and Y respectively
LABELS = ['A', 'B', 'X', 'Y']

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    label = LABELS[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))
    play_obj = wav_obj.play()
    play_obj.wait_done()


# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 100ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=100)

try:
    while True:
        # By using "time.time()" as the source of our hue value,
        # rather than incrementing a counter, we make sure the colour
        # transition effect speed is independent from the display framerate.
        hue = time.time() / 10

        # "hsv_to_rgb" converts our hue, saturation and value numbers
        # into the RGB colourspace needed for PIL's ImageDraw.
        # Since it returns floats from 0.0 to 1.0, we multiply them by 255
        # to get the RGB value range we're used to.
        r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]

        # We're just going to fill the whole screen with our colour.
        draw.rectangle((0, 0, 240, 240), (r, g, b))

        message = datetime.now().strftime('%H:%M:%S')
        size_x, size_y = draw.textsize(message, font)
        text_x = (st7789.width / 2) - (size_x / 2)
        text_y = (st7789.height / 2) - (size_y / 2)

        draw.text((text_x, text_y), message,
                  font=font, fill=(255, 255, 255), align='center')
        st7789.display(image)

        time.sleep(1.0 / 30)

# When you press ctrl+c, this will be called
finally:
    print('Finally.')
    sa.stop_all()
    GPIO.cleanup()
