import time
import board
import busio
import qwiic_twist

import paho.mqtt.client as mqtt
import uuid

myTwist = qwiic_twist.QwiicTwist()
myTwist.begin()
myTwist.count = 0

client = mqtt.Client(str(uuid.uuid1()))
client.tls_set()
client.username_pw_set('idd', 'device@theFarm')

client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

topic = 'IDD/cake'

i2c = busio.I2C(board.SCL, board.SDA)

while True:
    amount = myTwist.count*10
    if amount < 350:
        val = f"Oven not set. Set oven to 350 to continue."
        print(val, amount)
        client.publish(topic, val)
    if amount >= 350:
        val = f"Oven set!"
        print(val, amount)
        client.publish(topic, val)
    time.sleep(0.25)
