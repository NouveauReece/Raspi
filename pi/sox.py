## Plays silent noise over speakers to avoid pops
import subprocess

sox_process = None

def start_sox():
    global sox_process
    if sox_process is None or sox_process.poll() is not None:
        sox_process = subprocess.Popen([
            'play', '-n', '-c2', 'synth', 'brownnoise', 'vol', '0'
        ], env={**os.environ, 'PULSE_SINK': 'alsa_output.platform-soc_sound.stereo-fallback'})
        print("Sox started")

def stop_sox():
    global sox_process
    if sox_process and sox_process.poll() is None:
        sox_process.terminate()
        sox_process.wait()
        sox_process = None
        print("Sox stopped")

def restart_sox():
    stop_sox()
    start_sox()
