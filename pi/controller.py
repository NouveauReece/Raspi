import RPi.GPIO as GPIO

import re
import os
import sys
import time
import subprocess
import requests
import signal

from url import *
from gpio import *
from source import *

# Mopidy Port
PORT = 6680

# Supported commands
commands = {
    "play" : "core.playback.play",
    "pause" : "core.playback.pause",
    "next" : "core.playback.next",
    "prev" : "core.playback.previous",
    "stop" : "core.playback.stop",
    "add" : "core.tracklist.add",
    "clear" : "core.tracklist.clear",
    "shuffle" : "core.tracklist.shuffle",
    "mopidy_volume": "core.mixer.get_volume"
}

def make_request(method, params={}):
    # Setup headers
    headers = {
        'Content-Type': 'application/json',
    }
    # Setup json_data
    json_data = {
        'jsonrpc' : '2.0',
        'id' : 1,
        'method' : method,
        'params' : params,
    }
    # Mopidy post request
    res = requests.post(f"http://localhost:{PORT}/mopidy/rpc", json=json_data, headers=headers)
    return res

def convert_spotify_url(url):
    return f"spotify:{spotify_get_type(url)}:{spotify_get_id(url)}"

def convert_youtube_url(url):
    return f"youtube:{url}"

def send_message(method, url=""):
    spotify_uri = ""
    params = {}
    
    # Check url to see if it is a valid sptofiy url
    if method == "add" and url != "":
        try:
            mopidy_url = ""

            if is_spotify_url(url):
                mopidy_url = convert_spotify_url(url)
            elif is_youtube_url(url):
                mopidy_url = convert_youtube_url(url)
            else:
                print("Incorrect url format.")
                return
                
            params["uris"] = [mopidy_url]
        except ValueError as e:
            print(str(e))
            return
    
    # Make request
    res = make_request(commands[method], params)
    # User add a track and url was valid format but not a real spotify url
    if url != "" and res.json()['result'] == []:
        print("Something went wrong adding your url.\nThe url may be incorrect or you may not be connected to your music provider")
        return
    # User added a track and it was valid
    return res.json()

def get_playback_state():
    # Request state from mopidy server
    return make_request("core.playback.get_state").json()['result']

if __name__ == "__main__":
    try:
        init_gpio()
        
        # Poll mopidy
        while True:
            print("\033[33mChecking connection\033[39m")
            try:
                time.sleep(1)
                get_playback_state()
                break
            except Exception:
                pass

        # clear current mopidy queue
        send_message("clear")

        # set default speaker volumes
        set_volume('dac', 0.1)
        set_volume('builtin', 0.5)
        make_request("core.mixer.set_volume", {"volume" : 50})

        # set gpio callbacks
        GPIO_CALLBACK["switch_on"] = lambda: switch_to("dac")
        GPIO_CALLBACK["switch_off"] = lambda: switch_to("builtin")
        # set source to current switch value
        switch_changed(None)
        
        while True:
            command = input("\nEnter command: ").lower()
            url = ""
        
            if command == "q":
                break
            elif command == "mopidy_volume_set":
                volume = int(input("Enter a value [0-100]: "))
                volume = min(max(volume, 0), 100)
                make_request("core.mixer.set_volume", {"volume" : volume})
                continue
            elif command == "volume":
                sink = get_source()
                volume = float(get_volume(sink)) * 100
                print(f"Volume: {volume}")
                continue
            elif command == "volume_set":
                sink = get_source()
                volume = int(input("Enter a value [0-100]: "))
                volume = min(max(volume, 0), 100) / 100
                set_volume(sink, volume)
                continue
            elif command == "source":
                print(get_source())
                continue
            elif command == "switch":
                sink = input("Enter sink [dac|builtin]: ")
                switch_to(sink)
                continue
            elif command == "add":
                url = input("Enter url: ")
            elif command not in commands:
                print("Not a valid command!")
                continue
            
            res = send_message(command, url)
            print(res)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nGoodbye")


