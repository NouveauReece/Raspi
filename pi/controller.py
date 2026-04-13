import time
from playsound import playsound

from drfid import *
from gpio import *
from mopidy import *
from source import *
from sox import *

# Mopidy port
PORT = 6680

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
    sink = input("Enter sink [dac|builtin]: ")
    switch_to(sink)


# Terminal test commands
test_commands = {
    "drfid_read": test_drfid_read,
    "startup": test_startup,
    "volume": test_volume,
    "volume_set": test_volume_set,
    "source": test_source,
    "switch": test_switch,
}

if __name__ == "__main__":
    try:
        init_gpio()
        
        # Poll mopidy
        while not is_mopidy_connected():
            time.sleep(1)

        # clear current mopidy queue
        send_mopidy_message("clear")

        # play silent noise through speakers
        # start_sox('dac')
        
        # set default speaker volumes
        set_volume('dac', 0.3)
        set_volume('builtin', 0.5)
        make_mopidy_request("core.mixer.set_volume", {"volume" : 50})

        # set gpio callbacks
        GPIO_CALLBACK["switch_on"] = lambda: switch_to("dac")
        GPIO_CALLBACK["switch_off"] = lambda: switch_to("builtin")

        # set source to current switch value
        init_switch_state()
        
        while True:
            command = input("Enter command: ").lower()
            if command == "q":
                break
            elif command in test_commands:
                test_commands[command]()
            elif command in mopidy_commands:
                param = None
                if command == "add":
                    param = input("Enter url: ")
                elif command == "mopidy_volume_set":
                    param = input("Enter a value [0-100]: ")
                res = send_mopidy_message(command, param)
                print(res)
            else:
                print("Not a valid command!")
                continue
    except KeyboardInterrupt:
        print("Quitting...")
    finally:
        send_mopidy_message("clear")
        stop_sox()
        cleanup_gpio()
        print("\nGoodbye")
