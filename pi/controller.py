import time
from playsound import playsound

from drfid import *
from gpio import *
from mopidy import *
from rfid import *
from source import *
from sox import *

def test_drfid_read():
    drfid_str = drfid_read_string()
    print("Read:", drfid_str)

def test_startup():
    playsound("/home/raspi/sounds/startup.mp3")

def test_volume():
    sink = get_source()
    volume = float(get_volume(sink)) * 100
    print(f"Volume: {volume}")

def test_volume_set():
    sink = get_source()
    volume = int(input("Enter a value [0-100]: "))
    volume = min(max(volume, 0), 100) / 100
    set_volume(sink, volume)
def test_source():
    print(get_source())

def test_switch():
    sink = input("Enter sink [builtin|aux]: ")
    switch_to(sink)

def test_motor_spin():
    motor_spin()

def test_motor_stop():
    motor_stop()
    
# Terminal test commands
test_commands = {
    "drfid_read": test_drfid_read,
    "startup": test_startup,
    "volume": test_volume,
    "volume_set": test_volume_set,
    "source": test_source,
    "switch": test_switch,
    "motor_spin": test_motor_spin,
    "motor_stop": test_motor_stop,
}


def drfid_written():
    drfid_str = drfid_read_string()
    print("DRFID:", drfid_str)
    
    if drfid_str == 'startup':
        test_startup()

def rfid_written(read):
    print("RFID: " + read)

def mopidy_playback_callback(state):
    if state == 'playing':
        motor_spin()
    else:
        motor_stop()
    
if __name__ == "__main__":
    try:
        init_gpio()
        
        # Poll mopidy
        while not is_mopidy_connected():
            time.sleep(1)

        # clear current mopidy queue
        mopidy_clear()

        # play silent noise through speakers
        start_sox('builtin')
        
        # set default speaker volumes
        set_volume('builtin', 0.4)
        set_volume('aux', 0.5)
        switch_to('builtin')
        
        # set gpio callbacks
        GPIO_CALLBACK["source"] = toggle_source
        GPIO_CALLBACK["shuffle"] = mopidy_shuffle
        GPIO_CALLBACK["volume_up"] = lambda: volume_change(True)
        GPIO_CALLBACK["volume_dn"] = lambda: volume_change(False)
        GPIO_CALLBACK["prev"] = mopidy_prev
        GPIO_CALLBACK["play"] = mopidy_toggle_playback
        GPIO_CALLBACK["next"] = mopidy_next

        # start poll services
        poll_for_drfid_write(drfid_written)
        poll_for_rfid_write(rfid_written)
        poll_for_playback_state(mopidy_playback_callback)
        
        while True:
            command = input("Enter command: ").lower()
            if command == "q":
                break
            elif command in test_commands:
                test_commands[command]()
            elif command in mopidy_commands:
                if command == "add":
                    url = input("Enter url: ")
                    res = mopidy_commands["add"](url)
                elif command == "mopidy_volume_set":
                    volume = int(input("Enter a value [0-100]: ")) / 100
                    res = mopidy_commands["mopidy_volume_set"](volume)
                else:
                    res = mopidy_commands[command]()
                print(res)
            else:
                print("Not a valid command!")
                continue
    except KeyboardInterrupt:
        print("Quitting...")
    finally:
        mopidy_clear()
        stop_sox()
        cleanup_gpio()
        print("\nGoodbye")
