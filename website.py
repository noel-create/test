from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import threading
import time
import os
import cv2 #type: ignore
import numpy as np
from mss import mss
from pyngrok import ngrok  # type: ignore
import pyautogui
from discord_webhook import DiscordWebhook

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

button_states = {
    'Mouse Left': False,
    'Mouse Down': False,
    'Mouse Right': False,
    'Mouse Up': False,
    'Left Click': False,
    'Right Click': False,
    'Shutdown': False
}

def continuous_action(button_id):
    while button_states[button_id]:
        if button_id == 'Mouse Left':
            xx, yy = pyautogui.position()
            pyautogui.moveTo(xx - 30, yy)
        elif button_id == 'Mouse Up':
            xx, yy = pyautogui.position()
            pyautogui.moveTo(xx, yy - 30)
        elif button_id == 'Mouse Right':
            xx, yy = pyautogui.position()
            pyautogui.moveTo(xx + 30, yy)
        elif button_id == 'Mouse Down':
            xx, yy = pyautogui.position()
            pyautogui.moveTo(xx, yy + 30)
        elif button_id == 'Left Click':
            pyautogui.leftClick(duration=0.2)
            time.sleep(0.5)
        elif button_id == 'Right Click':
            pyautogui.rightClick(duration=0.2)
            time.sleep(0.5)
        elif button_id == 'Shutdown':
            time.sleep(2)
            os.system("shutdown /s /t 1")
        time.sleep(0.5)

def generate_live_stream():
    with mss() as sct:
        monitor = sct.monitors[1]  # Get the primary monitor (adjust if necessary)
        while True:
            # Capture the screen
            img = np.array(sct.grab(monitor))
            # Convert to BGR format for OpenCV
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            # Emit the frame over SocketIO
            socketio.emit('live_stream', frame)
            time.sleep(0.03)  # Adjust the sleep time to control frame rate (around 30 FPS)

@socketio.on('connect')
def handle_connect():
    emit('button_states', button_states)

@socketio.on('toggle_button')
def handle_toggle_button(data):
    button_id = data['buttonId']
    if button_id in button_states:
        button_states[button_id] = not button_states[button_id]
        if button_states[button_id]:
            action_thread = threading.Thread(target=continuous_action, args=(button_id,))
            action_thread.start()
        else:
            print(f'Button {button_id} is toggled off')
        emit('button_states', button_states, broadcast=True)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    stream_thread = threading.Thread(target=generate_live_stream)
    stream_thread.daemon = True
    stream_thread.start()

    public_url = ngrok.connect(5000)
    webhook = DiscordWebhook(url="YOUR_DISCORD_WEBHOOK_URL", content=f"Server is live on: {public_url}")
    webhook.execute()
    socketio.run(app, debug=False)
