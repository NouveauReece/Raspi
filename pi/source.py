import pulsectl
import subprocess
import sys

from sinks import SINKS
from mopidy import mopidy_volume_set

VOLUME_CHANGE = 0.05

source_volume = {
    'builtin': {
        'current': 0.4,
        'max': 0.8,
        'min': 0.2,
    },
    'aux': {
        'current': 0.5,
        'max': 1.0,
        'min': 0.2,
    },
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
        mopidy_volume_set(source_volume[sink_name]['current'])
        set_volume(sink_name, source_volume[sink_name]['current']) # unnecessary but eh

def toggle_source():
    sink = get_source()
    if sink == 'builtin':
        switch_to('aux')
    else:
        switch_to('builtin')
        
def set_volume(sink, volume):
    sink_name = SINKS[sink]['sink']
    with pulsectl.Pulse('volume-control') as pulse:
        for sink_obj in pulse.sink_list():
            if sink_obj.name == sink_name:
                source_volume[sink]['current'] = volume
                pulse.volume_set_all_chans(sink_obj, volume)
                return

def get_volume(sink):
    sink_name = SINKS[sink]['sink']
    with pulsectl.Pulse('volume-control') as pulse:
        for sink_obj in pulse.sink_list():
            if sink_obj.name == sink_name:
                return pulse.volume_get_all_chans(sink_obj)
    return None

def volume_change(inc=True):
    sink = get_source()
    volume = source_volume[sink]['current']
    change = VOLUME_CHANGE if inc else -1 * VOLUME_CHANGE
    set_volume(sink, min(source_volume[sink]['max'],
                         max(source_volume[sink]['min'],
                             volume + change)))
