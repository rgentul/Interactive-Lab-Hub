import enum
import os
import signal
import sys
import time

import digitalio
import board
import adafruit_rgb_display.st7789 as st7789
import busio
import qwiic_twist
import qwiic_button

from PIL import Image, ImageDraw, ImageFont
from subprocess import call, Popen

cwd = os.getcwd()

def speak(command):
    call(f"espeak -ven -k5 -s150 --stdout '{command}' | aplay", shell=True)
    time.sleep(0.5)

def display_image(img):
    display_img = Image.open(f'{cwd}/imgs/{img}')
    display_img = image_formatting(display_img, width, height)
    disp.image(display_img, rotation)

def get_user_input(correct_answer = 1, wrong_answer_prompt='Press Ctrl-C to exit. Otherwise, try again:'):
    decision = type(correct_answer)(input('Enter your choice: '))
    while decision != correct_answer:
        decision = type(correct_answer)(input(wrong_answer_prompt))
    return decision

def blink_button(button):
    while not button.is_button_pressed():
        button.LED_on(255)
        time.sleep(0.5)
        button.LED_off()
        time.sleep(0.5)
    button.LED_off()

def signal_handler(sig, frame):
    print('Closing Gracefully')
    audio_stream.terminate()
    sys.exit(0)

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

hardware = 'plughw:2,0'
audio_stream = Popen("/usr/bin/cvlc alsa://"+hardware+" --sout='#transcode{vcodec=none,acodec=mp3,ab=256,channels=2,samplerate=44100,scodec=none}:http{mux=mp3,dst=:8080/}' --no-sout-all --sout-keep", shell=True)


# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding

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

# Set up the rotary pin
twist = qwiic_twist.QwiicTwist()
twist.begin()
twist_count = 0
twist.set_blue(255)
twist.set_red(100)
twist.set_green(255)

# Set up buttons
redButton = qwiic_button.QwiicButton()
redButton.begin()

greenButton = qwiic_button.QwiicButton(address=0x62)
greenButton.begin()

# Configure screen buttons
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

def image_formatting(image2, width=240, height=135):
    image2 = image2.convert('RGB')
    # Scale the image to the smaller screen dimension
    image2 = image2.resize((width, height), Image.BICUBIC)
    return image2

houses = ['Gryffinndor', 'Hufflepuff', 'Ravenclaw', 'Slitherin']
class Scene(enum.Enum):
    WELCOME = 0
    ARE_YOU_READY = 1
    DIAGON_ALLEY = 2
    BRICK_IMAGE = 3
    OLLIVANDERS = 4
    CHOOSE_WAND = 5
    HOGWARTS_EXPRESS = 6
    BEANS = 7
    SUITCASE = 8
    USE_SPELL = 9
    SORTING_HAT = 10
    CHOOSE_HOUSE = 11
    THANK_YOU = 12

img_dict = {
    Scene.WELCOME: 'welcome_hogwarts.jpeg',
    Scene.ARE_YOU_READY: 'ready.png',
    Scene.DIAGON_ALLEY: 'diagon-alley.png',
    Scene.BRICK_IMAGE: 'puzzle.png', 
    Scene.OLLIVANDERS: 'ollivanders.jpg',
    Scene.CHOOSE_WAND: 'wands.jpeg',
    Scene.HOGWARTS_EXPRESS: 'hogwarts-express.jpg',
    Scene.BEANS: 'beans.png',
    Scene.SUITCASE: 'suitcase.jpg',
    Scene.USE_SPELL: 'open-suitcase.jpg',
    Scene.SORTING_HAT: 'great-hall.jpeg',
    Scene.CHOOSE_HOUSE: 'house-0.png',
    Scene.THANK_YOU: 'thankyou.png'
}

screen = Scene.WELCOME

while True:
    display_image(img_dict[screen])

    if screen == Scene.WELCOME:
        speak(f'We are pleased to inform that you have been admitted to Hogwarts School of Witchcraft and Wizardry!')
        speak(f'Before you join us next week, you are required to complete 5 tasks.')
        next_screen = Scene.ARE_YOU_READY

    if screen == Scene.ARE_YOU_READY:
        speak(f'Are you ready? Say YES or NO. Press the red button to repeat.')
        # TODO Add red button func
        get_user_input()
        next_screen = Scene.DIAGON_ALLEY
        time.sleep(0.1)

    if screen == Scene.DIAGON_ALLEY:
        speak(f'Your first task is to enter Diagon Alley')
        next_screen = Scene.BRICK_IMAGE

    if screen == Scene.BRICK_IMAGE:
        speak(f"Tap on the right brick to enter! Here is your clue.")
        speak(f"In this world, left means right and up means down!")
        speak(f"Start at 3,3. Move one step right, then left-up.")
        speak(f"Finally, move left down.")
        speak(f"Which brick did you land in?")
        speak(f"Press the green button when you're ready to answer. Press red to repeat.")

        while not (redButton.is_button_pressed() or greenButton.is_button_pressed()):
            redButton.LED_on(255); greenButton.LED_on(255)
            time.sleep(0.5)
            redButton.LED_off(); greenButton.LED_off()
            time.sleep(0.5)
        repeat = redButton.is_button_pressed()
        redButton.LED_off(); greenButton.LED_off()

        # blink_button(greenButton)
        if not repeat:
            answer = get_user_input(correct_answer='3,3', wrong_answer_prompt='Wrong Answer! Think again!')
            speak(f"Correct! Welcome to Diagon Alley.")
            next_screen = Scene.OLLIVANDERS

    if screen == Scene.OLLIVANDERS:
        speak(f'Task Number 2')
        speak(f'You definitely need a wand before you are off to learn magic!')
        speak(f'Let us find you one.')
        next_screen = Scene.CHOOSE_WAND

    if screen == Scene.CHOOSE_WAND:
        speak(f'Use 3 words to describe yourself!')
        speak(f'This will help Ollivander pick a wand for you.')

        speak(f"Press the green button when you're ready to answer. Press red to repeat.")

        while not (redButton.is_button_pressed() or greenButton.is_button_pressed()):
            redButton.LED_on(255); greenButton.LED_on(255)
            time.sleep(0.5)
            redButton.LED_off(); greenButton.LED_off()
            time.sleep(0.5)
        repeat = redButton.is_button_pressed()
        redButton.LED_off(); greenButton.LED_off()

        if not repeat:
            get_user_input()
            time.sleep(0.5)
            speak(f"Hmm! Wood from Black Walnut and a Core of Dragon Heartstring, that is perfect for you.")
            next_screen = Scene.HOGWARTS_EXPRESS

    if screen == Scene.HOGWARTS_EXPRESS:
        speak(f'Now that you have your wand, get aboard the Hogwarts Express!')
        speak(f'Enjoy your journey')
        time.sleep(1)
        speak(f'Looks like you are hungry.')
        speak(f'Let us buy Bertie Botts all flavour beans.')
        next_screen = Scene.BEANS
        
    if screen == Scene.BEANS:
        speak(f"Which flavours do you want?")
        choice = int(input('Enter your choice: '))
        while choice != 1:
            speak('Boring Choice! Try something unique')
            choice = int(input('Try something interesting:'))
        speak(f"Now, that is an interesting choice!")
        next_screen = Scene.SUITCASE
    
    if screen == Scene.SUITCASE:
        speak(f'Welcome to Hogwarts!')
        speak(f'Before you proceed to The Great Hall, you need to get dressed.')
        speak(f'But you forgot the keys to your suitcase at home.')
        speak(f'Try to remember and use the spell to open the lock!')
        next_screen = Scene.USE_SPELL
    
    if screen == Scene.USE_SPELL:
        choice = int(input('Enter your choice: '))
        while choice != 1:
            speak('Think harder! You can do this.')
            choice = int(input('Think again:'))

        speak(f"Good Memory! Now get changed quickly!")
        speak(f"Dinner is about to begin.")
        next_screen = Scene.SORTING_HAT
    
    if screen == Scene.SORTING_HAT:
        speak(f'Welcome to the great hall! Hogwarts has 4 houses.')
        speak(', '.join(houses))
        speak(f'Use the rotating wheel to choose your House.')
        next_screen = Scene.CHOOSE_HOUSE
    
    if screen == Scene.CHOOSE_HOUSE:
        speak(f'Press the wheel to confirm.')
        while not twist.is_pressed():
            choice = twist.count % 4
            display_image(f'house-{choice}.png')
            time.sleep(0.2)
        
        speak(f'What are the 2 colors that represent {houses[choice]}?')
        get_user_input(wrong_answer_prompt='Wrong answer try again.')
        speak(f"That is the correct answer!")
        speak(f'You are now part of {houses[choice]}.')
        next_screen = Scene.THANK_YOU

    if screen == Scene.THANK_YOU:
        time.sleep(0.5)
        speak(f'Thank you for playing!')
        speak(f'Good luck for your future at Hogwarts.')
        time.sleep(2)
        backlight.value = False
        break

    # Restart
    if buttonB.value and not buttonA.value:  # just button A pressed
        next_screen = Scene.WELCOME
    
    time.sleep(0.1)
    screen = next_screen

signal.signal(signal.SIGINT, signal_handler)
