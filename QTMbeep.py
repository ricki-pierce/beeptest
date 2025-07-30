#This code creates a start button which is to be used outside of QTM. When the start button is clicked, QTM immediately starts recording. At the same time the start button is clicked, there is 500 milliseconds
#of silence. Then there is a beep at 500Hz which plays for 500 milliseconds. This sound corresponds to teh 500 millisecond to 1000 millisecond interval of the QTM file. 

# ========== IMPORTING MODULES ==========
import asyncio                    # Lets us run asynchronous tasks (like waiting without freezing the app)
import threading                 # Allows tasks to run in the background without freezing the GUI
import numpy as np              # Library for working with arrays and math functions
import sounddevice as sd       # Lets us play audio from Python
import tkinter as tk           # Used to create GUI windows and buttons
from tkinter import messagebox # Allows pop-up message windows (for errors or info)
import qtm                     # Custom library to communicate with QTM motion capture system
import os                      # Used to interact with the file system (like changing folders)

# ========== SETTING WORKING DIRECTORY ==========
os.chdir("C:/Users/Ricki")  # Changes the current folder to this path so files and settings are loaded from here

# ========== GLOBAL VARIABLE ==========
qtm_connection = None  # This variable will store our connection to QTM; starts out as "None" (not connected)

# ========== FUNCTION TO START QTM RECORDING ==========
async def start_qtm_recording():
    global qtm_connection  # Use the global variable defined earlier
    try:
        qtm_connection = await qtm.connect("127.0.0.1")  # Try to connect to QTM on the same computer (localhost)
        print("Connected to QTM.")

        await qtm_connection.take_control("")  # Take control of QTM; assumes no password is needed

        await qtm_connection.start()  # Start the recording
        print("Recording started.")

    except Exception as e:
        # If something goes wrong, print the error and reset the connection to None
        print(f"Failed to start QTM recording: {e}")
        qtm_connection = None

# ========== FUNCTION TO PLAY A BEEP SOUND (BLOCKING) ==========
def play_beep_blocking():
    fs = 44100        # Sample rate: how many audio samples per second
    duration = 0.5    # Length of beep in seconds (0.5 sec = 500 milliseconds)
    frequency = 500   # Beep sound frequency in Hz

    # Create a time array from 0 to 0.5 sec
    t = np.linspace(0, duration, int(fs * duration), False)
    # Generate a sine wave for the beep sound
    beep = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Play the beep sound and wait until it's done
    sd.play(beep, fs)
    sd.wait()

# ========== COMBINED FUNCTION TO START RECORDING AND THEN BEEP ==========
async def start_recording_and_beep():
    await start_qtm_recording()  # Try to start recording

    if qtm_connection is None:
        # If connection failed, show an error pop-up window
        def show_error():
            messagebox.showerror("Error", "Failed to start recording.")
        root.after(0, show_error)  # Schedule error pop-up to show up in the GUI
        return

    # Wait 0.5 seconds (500 ms) to match the requirement of silence
    await asyncio.sleep(0.5)

    # Play the beep without freezing the app, by running it in a background thread
    await asyncio.to_thread(play_beep_blocking)

    # Do NOT stop the recording here. That will be handled by the Stop button.

# ========== START BUTTON FUNCTION ==========
def on_start_button():
    # This nested function will be run in a separate thread
    def runner():
        asyncio.run(start_recording_and_beep())  # Run the async function in a new event loop

    # Run the above function in a new background thread (so GUI stays responsive)
    threading.Thread(target=runner, daemon=True).start()

# ========== STOP BUTTON FUNCTION ==========
def on_stop_button():
    # Same idea: stop function will be run in the background
    def runner():
        asyncio.run(stop_recording())

    threading.Thread(target=runner, daemon=True).start()

# ========== FUNCTION TO STOP RECORDING ==========
async def stop_recording():
    global qtm_connection
    if qtm_connection:
        try:
            await qtm_connection.stop()  # Tell QTM to stop recording
            print("Recording stopped.")
            qtm_connection.disconnect()  # Close the connection
            print("Disconnected from QTM.")
            qtm_connection = None  # Reset global variable

        except Exception as e:
            # If there's an error, print it and show an error pop-up
            print(f"Failed to stop QTM recording: {e}")
            def show_error():
                messagebox.showerror("Error", "Failed to stop recording.")
            root.after(0, show_error)
    else:
        print("No active connection to stop.")  # If nothing was recording, do nothing

# ========== BUILDING THE GUI ==========
def build_gui():
    global root
    root = tk.Tk()  # Create the main window
    root.title("QTM Controller")  # Set window title

    # Create the Start button
    start_btn = tk.Button(root, text="Start Recording", command=on_start_button, width=25, height=3)
    start_btn.pack(pady=10, padx=20)  # Add button to window with spacing

    # Create the Stop button
    stop_btn = tk.Button(root, text="Stop Recording", command=on_stop_button, width=25, height=3)
    stop_btn.pack(pady=10, padx=20)

    root.mainloop()  # Start the GUI event loop (waits for user to interact)

# ========== MAIN ENTRY POINT ==========
if __name__ == "__main__":
    build_gui()  # When you run this file, it builds and opens the GUI window
