from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device

from drfid import drfid_setup

Device.pin_factory = LGPIOFactory()

SWITCH_PIN = 17
DRFID_GPO_PIN = 27

GPIO_CALLBACK = {
    "switch_on": (lambda: 0),
    "switch_off": (lambda: 0),
    "drfid_tag_written": (lambda: 0),
}

def init_gpio():
    global switch
    switch = Button(SWITCH_PIN, pull_up=True, bounce_time=0.3)
    switch.when_pressed = switch_on
    switch.when_released = switch_off

    drfid_setup()
    gpo = Button(DRFID_GPO_PIN, pull_up=True)
    gpo.when_pressed = drfid_tag_written
    
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
    
def drfid_tag_written():
    GPIO_CALLBACK["drfid_tag_written"]()
