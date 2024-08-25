from customtkinter import *
import pystray
from PIL import Image, ImageDraw
import sys
import threading
import keyboard

def minimize_to_tray():
    app.withdraw()

    def on_quit(icon, item):
        icon.stop()
        app.quit()
        sys.exit()

    def on_restore(icon, item):
        icon.stop()
        app.deiconify()

    icon_image = Image.new('RGB', (64, 64), (255, 0, 0))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle([16, 16, 48, 48], fill=(255, 255, 255))

    icon = pystray.Icon("test", icon_image, menu=pystray.Menu(
        pystray.MenuItem("Restore window", on_restore),
        pystray.MenuItem("Quit", on_quit)
    ))

    icon.run()

def quit():
    app.quit()
    sys.exit()

def on_minimize_click():
    threading.Thread(target=minimize_to_tray).start()

app = CTk()
app.geometry("500x400")

lab1 = CTkLabel(app, text="Tkinter test app")
lab1.place(relx=0.5, rely=0.4, anchor=CENTER)

minimize_button = CTkButton(app, text="Minimize to Tray", command=on_minimize_click)
minimize_button.place(relx=0.5, rely=0.6, anchor=CENTER)

quit_button = CTkButton(app, text="Exit", command=quit)
quit_button.place(relx=0.5, rely=0.75, anchor=CENTER)

app.mainloop()
