from gpiozero import Motor, Device
from gpiozero.tones import Tone
import time

ENA_PIN = 5  # GPIO pin connected to the EN1 pin L298N
IN1_PIN = 6  # GPIO pin connected to the IN1 pin L298N
IN2_PIN = 16  # GPIO pin connected to the IN2 pin L298N


# Create Motor object (gpiozero handles PWM and direction internally)
motor = Motor(forward=IN1_PIN, backward=IN2_PIN, enable=ENA_PIN, pwm=True)

# Main loop
try:
    while True:
        # Motor spins clockwise (forward)
        motor.forward(0)  # Start at 0 speed

        # Increase speed gradually
        for speed in range(0, 101):
            motor.forward(speed / 100)
            time.sleep(0.01)

        time.sleep(1)  # Rotate at maximum speed for 1 second in clockwise direction

        # Change direction to anti-clockwise (backward)
        motor.backward(1)  # Full speed backward

        time.sleep(1)  # Rotate at maximum speed for 1 second in anti-clockwise direction

        # Decrease speed gradually
        for speed in range(100, -1, -1):
            motor.backward(speed / 100)
            time.sleep(0.01)

        motor.stop()
        time.sleep(1)  # Stop motor for 1 second

except KeyboardInterrupt:
    pass

finally:
    motor.close()  # Release GPIO resources on program exit
