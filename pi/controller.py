import re
import os
import sys
import time
import subprocess
import requests
import signal

from url import *

# Mopidy Port
PORT = 6680

# Initial audio
Volume = 50

# Supported commands
commands = {
    "play" : "core.playback.play",
    "pause" : "core.playback.pause",
    "next" : "core.playback.next",
    "prev" : "core.playback.previous",
    "stop" : "core.playback.stop",
    "add" : "core.tracklist.add",
    "clear" : "core.tracklist.clear",
    "shuffle" : "core.tracklist.shuffle"
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
    print(res)
    print(res.json())
    # User add a track and url was valid format but not a real spotify url
    if url != "" and res.json()['result'] == []:
        print("Something went wrong adding your url.\nThe url may be incorrect or you may not be connected to your music provider")
        return
    # User added a track and it was valid
    print("Done sending message")

def get_playback_state():
    # Request state from mopidy server
    return make_request("core.playback.get_state").json()['result']

if __name__ == "__main__":

    # Poll mopidy
    while True:
        print("\033[33mChecking connection\033[39m")
        try:
            time.sleep(1)
            get_playback_state()
            break
        except Exception:
            pass

    send_message("clear")
    while True:
        command = input("\nEnter command: ")
        url = ""
        
        if command.lower() == "q":
            break
        if command.lower() == "add":
            url = input("Enter url: ")
        # Invalid command
        if command not in commands:
            print("Not a valid command!")
            continue
        
        send_message(command, url)

