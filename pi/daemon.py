import time
from playsound import playsound

from drfid import *
from gpio import *
from mopidy import *
from rfid import *
from source import *
from sox import *

def drfid_written():
    print("Dynamic RFID: " + drfid_read_string())

def rfid_written(read):
    print("RFID: " + read)

if __name__ == "__main__":
    try:
        init_gpio()
        
        # Poll mopidy
        while not is_mopidy_connected():
            time.sleep(1)

        # clear current mopidy queue
        send_mopidy_message("clear")

        # play silent noise through speakers
        start_sox('dac')
        
        # set default speaker volumes
        set_volume('dac', 0.3)
        set_volume('builtin', 0.5)
        make_mopidy_request("core.mixer.set_volume", {"volume" : 50})

        # set gpio callbacks
        GPIO_CALLBACK["switch_on"] = lambda: switch_to("dac")
        GPIO_CALLBACK["switch_off"] = lambda: switch_to("builtin")

        # set source to current switch value
        init_switch_state()

        poll_for_drfid_write(drfid_written)
        poll_for_rfid_write(rfid_written)
        
        while True:            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Quitting...")
    finally:
        send_mopidy_message("clear")
        stop_sox()
        cleanup_gpio()
        print("\nGoodbye")
