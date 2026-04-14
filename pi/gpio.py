from gpiozero import Button, Device, Motor
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

# Button pins
SOURCE_PIN = 17
SHUFFLE_PIN = 23
VOLUME_UP_PIN = 24
VOLUME_DN_PIN = 16
PREV_PIN = 19
PLAY_PIN = 20
PAUSE_PIN = 21

# Motor pins
ENA_PIN = 5
IN1_PIN = 6
IN2_PIN = 22


GPIO_CALLBACK = {
    "switch_on": (lambda: 0),
    "switch_off": (lambda: 0),
}

def init_gpio():
    global source, shuffle, volume_up, volume_dn, prev, play, pause, motor

    source = Button(SOURCE_PIN, pull_up=True, bounce_time=0.3)
    shuffle = Button(SHUFFLE_PIN, pull_up=True, bounce_time=0.3)
    volume_up = Button(VOLUME_UP_PIN, pull_up=True, bounce_time=0.3)
    # volume_dn = Button(VOLUME_DN_PIN, pull_up=True, bounce_time=0.3)
    # prev = Button(PREV_PIN, pull_up=True, bounce_time=0.3)
    play = Button(PLAY_PIN, pull_up=True, bounce_time=0.3)
    # pause = Button(PAUSE_PIN, pull_up=True, bounce_time=0.3)

    
    # switch.when_pressed = switch_on
    # switch.when_released = switch_off

    motor = Motor(forward=IN1_PIN, backward=IN2_PIN, enable=ENA_PIN, pwm=True)
    motor.stop()
    
    
def cleanup_gpio():
    global switch, motor
    if switch:
        switch.close()
    if motor:
        motor.close()
        
def switch_on():
    GPIO_CALLBACK["switch_on"]()

def switch_off():
    GPIO_CALLBACK["switch_off"]()

def motor_spin():
    motor.forward(1)

def motor_stop():
    motor.stop()
