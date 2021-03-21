from __future__ import print_function
import qwiic_button 
import time
import sys

from datetime import datetime, timedelta
import subprocess
import digitalio
import board
from time import strftime, sleep
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.st7789 as st7789
import webcolors

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
rotation = 90
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

clock = datetime.now()
timezone = 0
counter = 0
while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    clock = datetime.now() + timedelta(hours=timezone)
    
    #TODO: fill in here. You should be able to look in cli_clock.py and stats.py
    y = top
    draw.text((x,y), format(clock, '%H:%M:%S'), font=font, fill="#FFFFFF")
    y += font.getsize(str(clock))[1]
    draw.text((x,y), "Top adds hour", font=font, fill="#FFFFFF")
    y += font.getsize(str(clock))[1]
    draw.text((x,y), "Don't press lower button", font=font, fill="#FFFFFF")
   
    if buttonA.value and not buttonB.value:
       if counter == 0:
           y = top
           draw.rectangle((0, 0, width, height), outline=0, fill=0)
           timezone = timezone - 1
           clock = datetime.now() + timedelta(hours=timezone)
           draw.text((x,y), "Um, ok...", font=font, fill="#FFFFFF")
           y += font.getsize(str(clock))[1]
           draw.text((x,y), "Subtracted one hour", font=font, fill="#FFFFFF")
           counter += 1
       elif counter == 1:
           y = top
           draw.rectangle((0, 0, width, height), outline=0, fill=0)
           draw.text((x,y), "You really shouldn't.", font=font, fill="#FFFFFF")
           counter += 1
       elif counter == 2:
           y = top
           draw.rectangle((0, 0, width, height), outline=0, fill=0)
           draw.text((x,y), "Please.", font=font, fill="#FFFFFF")
           counter += 1
       elif counter == 3:
           y = top
           draw.rectangle((0, 0, width, height), outline=0, fill=0)
           draw.text((x,y), "Ok, fine. Do it again.", font=font, fill="#FFFFFF")
           counter += 1
       else:
           y = top
           draw.rectangle((0, 0, width, height), outline=0, fill=0)
           loan = Image.open("loan.jpg")
           image_ratio = loan.width / loan.height
           screen_ratio = width/height
           if screen_ratio < image_ratio:
              scaled_width = loan.width * height // loan.height
              scaled_height = height
           else:
              scaled_width = width
              scaled_height = loan.height * width // loan.width
           loan = loan.resize((scaled_width, scaled_height), Image.BICUBIC)
           x = scaled_width // 2 - width // 2
           y = scaled_height // 2 - height // 2
           loan = loan.crop((x, y, x + width, y + height))
           disp.image(loan, rotation)
           time.sleep(4)
           x = 0
           y = 0
    if buttonB.value and not buttonA.value:
       y = top
       draw.rectangle((0, 0, width, height), outline=0, fill=0)
       timezone = timezone + 1
       clock = datetime.now() + timedelta(hours=timezone)
       draw.text((x,y), "Added one hour", font=font, fill="#FFFFFF")
    if not buttonA.value and not buttonB.value:
       draw.text((x,y), clock, font=font, fill="#FFFFFF")
    # Display image.
    disp.image(image, rotation)
    time.sleep(1)

def run_example():

    print("\nSparkFun Qwiic Button Example 1")
    my_button = qwiic_button.QwiicButton()

    if my_button.begin() == False:
        print("\nThe Qwiic Button isn't connected to the system. Please check your connection", \
            file=sys.stderr)
        return
    print("\nButton ready!")
    
    while True:   
        
        if my_button.is_button_pressed() == True:
            print("\nThe button is pressed!")

        else:    
            print("\nThe button is not pressed!")
            
        time.sleep(0.02)

if __name__ == '__main__':
    try:
        run_example()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example 1")
        sys.exit(0)
