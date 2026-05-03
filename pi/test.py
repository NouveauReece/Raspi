from gpiozero import RGBLED
import time

RED_PIN = 4
GREEN_PIN = 14
BLUE_PIN = 15

rgb = RGBLED(red=RED_PIN, green=GREEN_PIN, blue=BLUE_PIN)

try:
    while True:
        rgb.color = (1,0,1)
except:
    rgb.off()
