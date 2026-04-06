## Plays silent noise over speakers to avoid pops
import subprocess
import os

from sinks import SINKS

soxes = []

def start_sox(sink):
    sox = subprocess.Popen(['play', '-n', '-c2', 'synth', 'brownnoise', 'vol', '0'],
                           env={**os.environ, 'PULSE_SINK': SINKS[sink]['sink']},
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    soxes.append(sox)
    print("Sox started")

def stop_sox():
    for sox in soxes:
        sox.kill()
