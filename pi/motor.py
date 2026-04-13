from gpiozero import Motor, Device
from gpiozero.tones import Tone
import time

ENA_PIN = 5  # GPIO pin connected to the EN1 pin L298N
IN1_PIN = 6  # GPIO pin connected to the IN1 pin L298N
IN2_PIN = 22  # GPIO pin connected to the IN2 pin L298N


# Create Motor object (gpiozero handles PWM and direction internally)
motor = Motor(forward=IN1_PIN, backward=IN2_PIN, enable=ENA_PIN, pwm=True)

# Main loop
try:
    while True:
        motor.forward(1)
        
except KeyboardInterrupt:
    pass

finally:
    motor.close()  # Release GPIO resources on program exit
