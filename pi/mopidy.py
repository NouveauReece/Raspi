import requests

from url import *

# Mopidy port
PORT = 6680

# Supported mopidy commands
mopidy_commands = {
    "play" : "core.playback.play",
    "pause" : "core.playback.pause",
    "next" : "core.playback.next",
    "prev" : "core.playback.previous",
    "stop" : "core.playback.stop",
    "add" : "core.tracklist.add",
    "clear" : "core.tracklist.clear",
    "shuffle" : "core.tracklist.shuffle",
    "mopidy_volume": "core.mixer.get_volume",
    "mopidy_volume_set": "core.mixer.set_volume",
}

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
    return res

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
    return res.json()

def get_playback_state():
    # Request state from mopidy server
    return make_mopidy_request("core.playback.get_state").json()['result']


def is_mopidy_connected():
    print("\033[33mChecking connection\033[39m")
    try:
        get_playback_state()
        return True
    except Exception:
        return False


def poll_for_playback_state(callback, interval=5):
    def _poll():
        while True:
            callback(get_playback_state())
            time.sleep(interval)
            
    t = threading.Thread(target=_poll, daemon=True)
    t.start()
