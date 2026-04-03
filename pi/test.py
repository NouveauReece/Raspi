import RPi.GPIO as GPIO
import time

SWITCH_PIN = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def switch_changed(channel):
    if GPIO.input(SWITCH_PIN) == GPIO.LOW:
        print("Switch flicked ON")
        # do something here
    else:
        print("Switch flicked OFF")
        # do something else here

GPIO.add_event_detect(SWITCH_PIN, GPIO.BOTH,
                      callback=switch_changed,
                      bouncetime=300)

print("Listening for switch changes...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
