import RPi.GPIO as GPIO
import time

SWITCH_PIN = 17

GPIO_CALLBACK = {
    "switch_on" : (lambda: 0),
    "switch_off" : (lambda: 0)
}

def switch_changed(channel):
    if GPIO.input(SWITCH_PIN) == GPIO.LOW:
        print("Switch flicked ON")
        GPIO_CALLBACK["switch_on"]()
    else:
        print("Switch flicked OFF")
        GPIO_CALLBACK["switch_off"]()

def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(SWITCH_PIN, GPIO.BOTH,
                          callback=switch_changed,
                          bouncetime=300)
