import subprocess
import atexit
from flask import Flask, render_template, jsonify, request
from pythonosc.udp_client import SimpleUDPClient

app = Flask(__name__)

# SuperCollider OSC configuration
SC_IP = "127.0.0.1"
SC_PORT = 57120
osc_client = SimpleUDPClient(SC_IP, SC_PORT)

audio_is_playing = False
sc_process = None

def boot_supercollider():
    """Spawns sclang with the noise machine script in the background."""
    global sc_process
    print("Spawning headless SuperCollider process...")
    try:
        # Executes: sclang noise_machine.scd
        sc_process = subprocess.Popen(
            ['sclang', 'noise_machine.scd'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("SuperCollider process initialized.")
    except FileNotFoundError:
        print("ERROR: 'sclang' command not found. Is SuperCollider installed?")

def cleanup_supercollider():
    """Ensures SuperCollider terminates when the Python script exits."""
    global sc_process
    if sc_process:
        print("Terminating SuperCollider background process...")
        sc_process.terminate()
        sc_process.wait()

# Register the cleanup function to prevent runaway background audio processes
atexit.register(cleanup_supercollider)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle', methods=['POST'])
def toggle_audio():
    global audio_is_playing
    audio_is_playing = not audio_is_playing
    
    if audio_is_playing:
        print("Sending OSC: /machine/play")
        osc_client.send_message("/machine/play", 1)
    else:
        print("Sending OSC: /machine/stop")
        osc_client.send_message("/machine/stop", 1)
        
    return jsonify({"status": "success", "isPlaying": audio_is_playing})

if __name__ == '__main__':
    # Boot SuperCollider right before starting the web server loop
    boot_supercollider()
    
    # Run Flask (Disable debug mode or use_reloader=False if it boots SC twice!)
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
