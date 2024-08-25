import pyautogui
import time
import os

time.sleep(1)

static_path = "static/images/screenshot.png"

while True:
    screenshot = pyautogui.screenshot("screenshot.png")
    screenshot.save(static_path)
    time.sleep(0.1)