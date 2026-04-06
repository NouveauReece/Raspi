import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

# text = "hello_world"
# id, text_written = reader.write(text)
# print(f"ID: {id}")
# print(f"Text Written: {text_written}")

id, text = reader.read()
print(f"ID: {id}")
print(f"Text: {text}")

GPIO.cleanup()
