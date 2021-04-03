#!/usr/bin/env python
#-----------------------------------------------------------------------------
# qwiic_twist_ex2.py
#
# Simple Example for the Qwiic Twist Device
#------------------------------------------------------------------------
#
# Written by  SparkFun Electronics, May 2019
# 
# This python library supports the SparkFun Electroncis qwiic 
# qwiic sensor/board ecosystem on a Raspberry Pi (and compatable) single
# board computers. 
#
# More information on qwiic is at https://www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#
#==================================================================================
# Copyright (c) 2019 SparkFun Electronics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.
#==================================================================================
# Example 2
#

from __future__ import print_function
import qwiic_twist
import qwiic_button
import time
import random

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

myTwist = qwiic_twist.QwiicTwist()

def brewMaster():

	print("\nStarting program\n")

	if myTwist.connected == False:
		print("The Qwiic twist device isn't connected to the system. Please check your connection", \
			file=sys.stderr)
		return

	myTwist.begin()

	while True:

		#print("Count: %d, Pressed: %s" % (myTwist.count, \
		#	"YES" if myTwist.pressed else "NO", \
		#	))

		#myTwist.set_color( random.randint(0,256), random.randint(0,256),random.randint(0,256))
		draw.rectangle((0, 0, width, height), outline=0, fill=0)

    		#TODO: fill in here. You should be able to look in cli_clock.py and stats.py
		y = top
		draw.text((x,y), "Welcome to the", font=font, fill="#FFFFFF")
		y += font.getsize("A")[1]
		draw.text((x,y), "PourOverMate 6000!", font=font, fill="#00FF1E")
		y += font.getsize("A")[1]
		draw.text((x,y), "\nPress stick to continue.", font=font, fill="#FFFFFF")
		y += font.getsize("A")[1]
		
		if myTwist.pressed:
			coffeeAmount = setAmount()
			print("back home! coffee amount: " + str(coffeeAmount))
			time.sleep(1)
			calculate(coffeeAmount)
			print("beans measured!")
			

		# Display image.
		disp.image(image, rotation)

		time.sleep(.1)
		
def setAmount():
	
	print("In setup but not while loop")
	myTwist.count = 0
	amount = 0
	time.sleep(1)
	
	while True:
		
		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		y = top
		draw.text((x,y), "How much coffee would", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), "you like? Turn dial to set.", font=font, fill="#FFFFFF")
		
		
		#print("%d ml, Pressed: %s" % (myTwist.count, \
		#	"YES" if myTwist.pressed else "NO", \
		#	))
		
		y += font.getsize("y")[1]
		draw.text((x,y),str(myTwist.count*10) + " milliliters", font=font, fill="#FF0000")
		y += font.getsize("y")[1]
		draw.text((x,y), "250ml in a standard cup.", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), "Press stick to confirm.", font=font, fill="#FFFFFF")
		
		if myTwist.pressed:
			amount = myTwist.count*10
			return amount
		
		disp.image(image, rotation)
		
		time.sleep(.1)
		
def calculate(coffeeAmount):
	
	beans = coffeeAmount * 0.06

	while True:
		#print("in calculate!")
		
		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		y = top
		draw.text((x,y), "You're brewing with", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), str(coffeeAmount) + " millilters", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), "Measure " + str(beans) + " grams", font=font, fill="#FF0000")
		y += font.getsize("y")[1]
		draw.text((x,y), "of beans for ideal brew", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), "Measure beans in hopper.", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), "Press stick when done.", font=font, fill="#FFFFFF")
		
		if myTwist.pressed:
			ready(beans, coffeeAmount)
		
		disp.image(image, rotation)
		
		time.sleep(.1)
		
def ready(beans, coffeeAmount):
	
	my_button = qwiic_button.QwiicButton()
	my_button.LED_on(80)
	
	while True:
	
		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		y = top
		draw.text((x,y), "You should have:", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), str(coffeeAmount) + "ml boiling water", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), str(beans) + " grams of beans", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), "If ready, grind beans.", font=font, fill="#FFFFFF")
		y += font.getsize("y")[1]
		draw.text((x,y), "Press button to start brew.", font=font, fill="#009933")
		
		if my_button.is_button_pressed() == True:
			print("button pressed!")
			draw.rectangle((0, 0, width, height), outline=0, fill=0)
			y = top
			draw.text((x,y), "Beginning timer in 3, 2, 1...", font=font, fill="#FFFFFF")
			disp.image(image, rotation)
			time.sleep(5)
			my_button.LED_off()
			timer(beans, coffeeAmount)
		
		disp.image(image, rotation)
		
		time.sleep(.1)

def timer(beans, coffeeAmount):
		
	now = time.time()
	future = now + 30
	while time.time() < future:
		print(future)
	
if __name__ == '__main__':
	try:
		brewMaster()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nWomp womp, ending program")
		sys.exit(0)
