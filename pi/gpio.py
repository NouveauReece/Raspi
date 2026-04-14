from gpiozero import Button, Device, OutputDevice
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

GPIO_CALLBACK = {
    "source": (lambda: print("unset")),
    "shuffle": (lambda: None),
    "volume_up": (lambda: None),
    "volume_dn": (lambda: None),
    "prev": (lambda: None),
    "play": (lambda: None),
    "next": (lambda: None),
}

def init_gpio():
    source_btn = Button(SOURCE_PIN, pull_up=True, bounce_time=0.05)
    shuffle_btn = Button(SHUFFLE_PIN, pull_up=True, bounce_time=0.05)
    volume_up_btn = Button(VOLUME_UP_PIN, pull_up=True, bounce_time=0.05)
    volume_dn_btn = Button(VOLUME_DN_PIN, pull_up=True, bounce_time=0.05)
    prev_btn = Button(PREV_PIN, pull_up=True, bounce_time=0.05)
    play_btn = Button(PLAY_PIN, pull_up=True, bounce_time=0.05)
    next_btn = Button(NEXT_PIN, pull_up=True, bounce_time=0.05)

    motor = OutputDevice(IN1_PIN)

    source_btn.when_pressed = lambda: GPIO_CALLBACK["source"]()
    shuffle_btn.when_pressed = lambda: GPIO_CALLBACK["shuffle"]()
    volume_up_btn.when_pressed = lambda: GPIO_CALLBACK["volume_up"]()
    volume_dn_btn.when_pressed = lambda: GPIO_CALLBACK["volume_dn"]()
    prev_btn.when_pressed = lambda: GPIO_CALLBACK["prev"]()
    play_btn.when_pressed = lambda: GPIO_CALLBACK["play"]()
    next_btn.when_pressed = lambda: GPIO_CALLBACK["next"]()
    
    # switch.when_pressed = switch_on
    # switch.when_released = switch_off

    # motor = Motor(forward=IN1_PIN, backward=IN2_PIN, enable=ENA_PIN, pwm=True)
    motor.off()

    GPIO_DEVICES["source"] = source_btn
    GPIO_DEVICES["shuffle"] = shuffle_btn
    GPIO_DEVICES["volume_up"] = volume_up_btn
    GPIO_DEVICES["volume_dn"] = volume_dn_btn
    GPIO_DEVICES["prev"] = prev_btn
    GPIO_DEVICES["play"] = play_btn
    GPIO_DEVICES["next"] = next_btn
    GPIO_DEVICES["motor"] = motor
    
    
def cleanup_gpio():
    if GPIO_DEVICES["motor"]:
        GPIO_DEVICES["motor"].off()

    for dev in GPIO_DEVICES:
        GPIO_DEVICES[dev].close()
        
def motor_spin():
    GPIO_DEVICES["motor"].on()

def motor_stop():
    GPIO_DEVICES["motor"].off()
