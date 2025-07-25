import asyncio
import threading
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import messagebox
import qtm
import os

os.chdir("C:/Users/Ricki")

# Global connection object
qtm_connection = None

async def start_qtm_recording():
    global qtm_connection
    try:
        qtm_connection = await qtm.connect("127.0.0.1")
        print("Connected to QTM.")

        await qtm_connection.take_control("")  # Assume empty password

        # Start recording
        await qtm_connection.start()
        print("Recording started.")

    except Exception as e:
        print(f"Failed to start QTM recording: {e}")
        qtm_connection = None

def play_beep_blocking():
    fs = 44100  # Sample rate
    duration = 0.5  # seconds
    frequency = 500  # Hz

    t = np.linspace(0, duration, int(fs * duration), False)
    beep = 0.5 * np.sin(2 * np.pi * frequency * t)

    sd.play(beep, fs)
    sd.wait()

async def start_recording_and_beep():
    await start_qtm_recording()
    if qtm_connection is None:
        def show_error():
            messagebox.showerror("Error", "Failed to start recording.")
        root.after(0, show_error)
        return

    # Beep after brief delay
    await asyncio.sleep(0.5)
    await asyncio.to_thread(play_beep_blocking)

    # DO NOT stop or disconnect here — wait for Stop button to do that

def on_start_button():
    def runner():
        asyncio.run(start_recording_and_beep())

    threading.Thread(target=runner, daemon=True).start()

def on_stop_button():
    def runner():
        asyncio.run(stop_recording())

    threading.Thread(target=runner, daemon=True).start()

async def stop_recording():
    global qtm_connection
    if qtm_connection:
        try:
            await qtm_connection.stop()
            print("Recording stopped.")
            qtm_connection.disconnect()
            print("Disconnected from QTM.")
            qtm_connection = None
        except Exception as e:
            print(f"Failed to stop QTM recording: {e}")
            def show_error():
                messagebox.showerror("Error", "Failed to stop recording.")
            root.after(0, show_error)
    else:
        print("No active connection to stop.")

def build_gui():
    global root
    root = tk.Tk()
    root.title("QTM Controller")

    start_btn = tk.Button(root, text="Start Recording", command=on_start_button, width=25, height=3)
    start_btn.pack(pady=10, padx=20)

    stop_btn = tk.Button(root, text="Stop Recording", command=on_stop_button, width=25, height=3)
    stop_btn.pack(pady=10, padx=20)

    root.mainloop()

if __name__ == "__main__":
    build_gui()
