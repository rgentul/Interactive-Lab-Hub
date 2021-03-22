from __future__ import print_function
import qwiic_button 
import time
import sys

import busio
import enum
import os
import signal
from subprocess import call, Popen

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

def speak(command):
    call(f"espeak -ven -k5 -s150 --stdout '{command}' | aplay", shell=True)
    time.sleep(0.5)
    
def new_jersey():
    answer = None
    my_button = qwiic_button.QwiicButton()
    print("in new jersey")
    y = top
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x,y), "NJ is the best state", font=font, fill="#FFFFFF")
    disp.image(image, rotation)
    speak(f'New Jersey is the best state.')
    time.sleep(1)
    speak(f'Enter your answer now.')
    t_end = time.time() + 10
    while time.time() < t_end:
        if my_button.is_button_pressed() == True:
            answer = True
            return answer
    answer = False
    return answer

def poodle():
    answer = None
    my_button = qwiic_button.QwiicButton()
    print("in poodle")
    y = top
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((x,y), "No one respectable owns", font=font, fill="#FFFFFF")
    y += font.getsize("A")[1]
    draw.text((x,y), "a poodle.", font=font, fill="#FFFFFF")
    disp.image(image, rotation)
    speak(f'No one respectable owns a poodle.')
    time.sleep(1)
    speak(f'Enter your answer now.')
    t_end = time.time() + 10
    while time.time() < t_end:
        if my_button.is_button_pressed() == True:
            answer = True
            return answer
    answer = False
    return answer

def run_example():
    
    stage = 0
    
    print("\nSparkFun Qwiic Button Example 1")
    my_button = qwiic_button.QwiicButton()

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    #TODO: fill in here. You should be able to look in cli_clock.py and stats.py
    y = top
    draw.text((x,y), "Get your finger ready!", font=font, fill="#FFFFFF")
    
    # Display image.
    disp.image(image, rotation)
    time.sleep(3)
    
    if my_button.begin() == False:
        print("\nThe Qwiic Button isn't connected to the system. Please check your connection", \
            file=sys.stderr)
        return
    print("\nButton ready!")
    
    if stage == 0: 
        while True:   
            if my_button.is_button_pressed() == False: 
                y = top
                draw.rectangle((0, 0, width, height), outline=0, fill=0)
                draw.text((x,y), "Answer correctly to win.", font=font, fill="#FFFFFF")
                y += font.getsize("A")[1]
                draw.text((x,y), "One press = True", font=font, fill="#FFFFFF")
                y += font.getsize("A")[1]
                draw.text((x,y), "If False, don't press.", font=font, fill="#FFFFFF")
                y += font.getsize("A")[1]
                draw.text((x,y), "10 secs per question", font=font, fill="#FFFFFF")
                y += font.getsize("A")[1]
                disp.image(image, rotation)
                speak(f'Press button to begin.')
            else:
                break
        firstQ = new_jersey()
        if firstQ == False:
            print("dummy, you lose.")
        if firstQ == True:
            print("Huzzah!")
            stage += 1
            
    if stage == 1:
        y = top
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((x,y), "Correct. Next question.", font=font, fill="#FFFFFF")
        disp.image(image, rotation)
        time.sleep(2)
        secondQ = poodle()
        if secondQ == True:
            print("dummy, you lose.")
            speak(f'No. You could not have been more wrong.')
        if secondQ == False:
            print("Huzzah!")
            stage += 1
            
    #if stage == 2:
        

if __name__ == '__main__':
    try:
        run_example()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("\nEnding Example 1")
        sys.exit(0)
