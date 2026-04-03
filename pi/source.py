import pulsectl
import subprocess
import sys

SINKS = {
    'dac' : {
        'label': 'HifiBerry DAC',
        'sink': 'alsa_output.platform-soc_sound.stereo-fallback'
    },
    'builtin' : {
        'label': 'Built-in speakers',
        'sink': 'alsa_output.0.stereo-fallback'
    }
}

def get_source():
    sink = subprocess.check_output(['pactl', 'get-default-sink']).decode().strip()
    for sink_label in SINKS:
        if sink == SINKS[sink_label]['sink']:
            return sink_label
    return f"unknown source: {sink}"

def switch_to(sink_name):
    if sink_name in SINKS:
        subprocess.run(['pactl', 'set-default-sink', SINKS[sink_name]['sink']])
        print(f"Switched to {SINKS[sink_name]['label']} (default updated)")
    else:
        print(f"Unknown sink: {sink_name}")
    
def set_volume(sink, volume):
    sink_name = SINKS[sink]['sink']
    with pulsectl.Pulse('volume-control') as pulse:
        for sink_obj in pulse.sink_list():
            if sink_obj.name == sink_name:
                pulse.volume_set_all_chans(sink_obj, volume)
                return
        print(f"Sink {sink_name} not found")

def get_volume(sink):
    sink_name = SINKS[sink]['sink']
    with pulsectl.Pulse('volume-control') as pulse:
        for sink_obj in pulse.sink_list():
            if sink_obj.name == sink_name:
                return pulse.volume_get_all_chans(sink_obj)
    return None
