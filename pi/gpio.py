from gpiozero import Button, Device, OutputDevice, RotaryEncoder
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

# Button pins
SOURCE_PIN = 17
SHUFFLE_PIN = 23
VOLUME_UP_PIN = 22
VOLUME_DN_PIN = 24
PREV_PIN = 5
PLAY_PIN = 20
NEXT_PIN = 27

# Motor pins
IN1_PIN = 6

GPIO_DEVICES = {}

def _gpio_not_set(pin):
    return lambda: print(f"GPIO pin {pin} callback not set")

GPIO_CALLBACK = {
    "source_on": _gpio_not_set("source_on"),
    "source_off": _gpio_not_set("source_off"),
    "shuffle": _gpio_not_set("shuffle"),
    "volume_up": _gpio_not_set("volume_up"),
    "volume_dn": _gpio_not_set("volume_dn"),
    "prev": _gpio_not_set("prev"),
    "play": _gpio_not_set("play"),
    "next": _gpio_not_set("next"),
}

def init_gpio():
    source_btn = Button(SOURCE_PIN, pull_up=True, bounce_time=0.05)
    shuffle_btn = Button(SHUFFLE_PIN, pull_up=True, bounce_time=0.05)
    prev_btn = Button(PREV_PIN, pull_up=True, bounce_time=0.05)
    play_btn = Button(PLAY_PIN, pull_up=True, bounce_time=0.05)
    next_btn = Button(NEXT_PIN, pull_up=True, bounce_time=0.05)
    volume = RotaryEncoder(VOLUME_DN_PIN, VOLUME_UP_PIN)
    motor = OutputDevice(IN1_PIN)

    source_btn.when_pressed = lambda: GPIO_CALLBACK["source_on"]()
    source_btn.when_released = lambda: GPIO_CALLBACK["source_off"]()
    shuffle_btn.when_pressed = lambda: GPIO_CALLBACK["shuffle"]()
    volume.when_rotated_clockwise = lambda: GPIO_CALLBACK["volume_up"]()
    volume.when_rotated_counter_clockwise = lambda: GPIO_CALLBACK["volume_dn"]()
    prev_btn.when_pressed = lambda: GPIO_CALLBACK["prev"]()
    play_btn.when_pressed = lambda: GPIO_CALLBACK["play"]()
    next_btn.when_pressed = lambda: GPIO_CALLBACK["next"]()
    
    motor.off()

    GPIO_DEVICES["source"] = source_btn
    GPIO_DEVICES["shuffle"] = shuffle_btn
    GPIO_DEVICES["volume"] = volume
    GPIO_DEVICES["prev"] = prev_btn
    GPIO_DEVICES["play"] = play_btn
    GPIO_DEVICES["next"] = next_btn
    GPIO_DEVICES["motor"] = motor
    
    
def cleanup_gpio():
    if GPIO_DEVICES["motor"]:
        GPIO_DEVICES["motor"].off()

    for dev in GPIO_DEVICES:
        GPIO_DEVICES[dev].close()

def init_switch_state():
    if GPIO_DEVICES["source"].is_pressed:
        GPIO_CALLBACK["source_on"]()
    else:
        GPIO_CALLBACK["source_off"]()
        
def motor_spin():
    GPIO_DEVICES["motor"].on()

def motor_stop():
    GPIO_DEVICES["motor"].off()
