from flask import Flask, render_template, jsonify, request
from pythonosc.udp_client import SimpleUDPClient

app = Flask(__name__)

# SuperCollider OSC configuration
# Since Python and SuperCollider run on the same Pi hardware, 127.0.0.1 is perfect.
SC_IP = "127.0.0.1"
SC_PORT = 57120
osc_client = SimpleUDPClient(SC_IP, SC_PORT)

# Tracks state locally to keep the UI toggle synced
audio_is_playing = False

@app.route('/')
def index():
    """Serves the main control webpage."""
    return render_template('index.html')

@app.route('/toggle', methods=['POST'])
def toggle_audio():
    """Handles the play/stop toggle from the webpage and fires OSC to SC."""
    global audio_is_playing
    
    # Toggle the state boolean
    audio_is_playing = not audio_is_playing
    
    if audio_is_playing:
        print("Sending OSC: /machine/play")
        osc_client.send_message("/machine/play", 1)
    else:
        print("Sending OSC: /machine/stop")
        osc_client.send_message("/machine/stop", 1)
        
    return jsonify({"status": "success", "isPlaying": audio_is_playing})

if __name__ == '__main__':
    # Host on 0.0.0.0 allows any tablet or phone on your local network to connect
    app.run(host='0.0.0.0', port=5000, debug=True)
