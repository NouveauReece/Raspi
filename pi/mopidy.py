import requests
import threading
import time

from gpio import motor_spin, motor_stop
from url import *

# Mopidy port
PORT = 6680

def make_mopidy_request(method, params={}):
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
    return res.json()['result']

def convert_spotify_url(url):
    return f"spotify:{spotify_get_type(url)}:{spotify_get_id(url)}"

def convert_youtube_url(url):
    return f"youtube:{url}"

def send_mopidy_message(method, param=None):
    spotify_uri = ""
    params = {}

    if method == "add" and param != None:
        try:
            mopidy_url = ""
            url = param

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
    elif method == "mopidy_volume_set" and param != None:        
        volume = min(max(int(param), 0), 100)
        params["volume"] = volume
    
    res = make_mopidy_request(mopidy_commands[method], params)
    if param != None and res.json()['result'] == []:
        print("Something went wrong...")
        return
    return res

def mopidy_play():
    return make_mopidy_request("core.playback.play")
def mopidy_pause():
    return make_mopidy_request("core.playback.pause")
def mopidy_next():
    return make_mopidy_request("core.playback.next")
def mopidy_prev():
    return make_mopidy_request("core.playback.prev")
def mopidy_stop():
    return make_mopidy_request("core.playback.stop")
def mopidy_add(url):
    mopidy_url = ""
    try:    
        if is_spotify_url(url):
            mopidy_url = convert_spotify_url(url)
        elif is_youtube_url(url):
            mopidy_url = convert_youtube_url(url)
        else:
            print("Incorrect url format.")
            return
    except ValueError as e:
        print(str(e))
        return
    return make_mopidy_request("core.tracklist.add", {"uris" : [mopidy_url]})
def mopidy_clear():
    return make_mopidy_request("core.tracklist.clear")
def mopidy_shuffle():
    return make_mopidy_request("core.tracklist.shuffle")
def mopidy_volume():
    return make_mopidy_request("core.mixer.get_volume")
def mopidy_volume_set(volume):
    volume = int(min(100, max(0, volume * 100)))
    return make_mopidy_request("core.mixer.set_volume", {"volume" : volume})
def mopidy_playback():
    return make_mopidy_request("core.playback.get_state")


def mopidy_toggle_playback():
    state = mopidy_playback()
    if state == "playing":
        mopidy_pause()
        motor_stop()
    else:
        mopidy_play()
        motor_spin()
    
def is_mopidy_connected():
    print("\033[33mChecking connection\033[39m")
    try:
        mopidy_playback()
        print("\033[32mConnected!\033[39m")
        return True
    except Exception as e:
        return False


def poll_for_playback_state(callback, interval=5):
    def _poll():
        while True:
            callback(mopidy_playback())
            time.sleep(interval)
            
    t = threading.Thread(target=_poll, daemon=True)
    t.start()


# Supported mopidy commands
mopidy_commands = {
    "play" : mopidy_play,
    "pause" : mopidy_pause,
    "next" : mopidy_next,
    "prev" : mopidy_prev,
    "stop" : mopidy_stop,
    "add" : mopidy_add,
    "clear" : mopidy_clear,
    "shuffle" : mopidy_shuffle,
    "mopidy_volume": mopidy_volume,
    "mopidy_volume_set": mopidy_volume_set,
}
