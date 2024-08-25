import pyautogui
import time
import os

time.sleep(1)

static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'screenshot.png',)

while True:
    screenshot = pyautogui.screenshot("screenshot.png")
    screenshot.save(static_path)
    time.sleep(0.1)