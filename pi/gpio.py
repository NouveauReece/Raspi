from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device

Device.pin_factory = LGPIOFactory()

SWITCH_PIN = 17

GPIO_CALLBACK = {
    "switch_on": (lambda: 0),
    "switch_off": (lambda: 0),
}

def init_gpio():
    global switch
    switch = Button(SWITCH_PIN, pull_up=True, bounce_time=0.3)
    switch.when_pressed = switch_on
    switch.when_released = switch_off
    
def cleanup_gpio():
    global switch
    if switch:
        switch.close()

switch = None

def switch_on():
    GPIO_CALLBACK["switch_on"]()

def switch_off():
    GPIO_CALLBACK["switch_off"]()

def init_switch_state():
    if switch.is_pressed:
        switch_on()
    else:
        switch_off()
