from gpiozero import RGBLED
import time

RED_PIN = 4
GREEN_PIN = 14
BLUE_PIN = 15

rgb = RGBLED(red=RED_PIN, green=GREEN_PIN, blue=BLUE_PIN)

colors = [(1,0,0), (0,1,0), (0,0,1), (1,1,0), (0,1,1), (1,0,1), (1,1,1)]

for c in colors:
    rgb.color = c
    time.sleep(1)

rgb.off()
