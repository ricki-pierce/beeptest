# Import asynchronous programming module
import asyncio

# Import threading for running functions in separate threads
import threading

# Import numpy for numerical operations
import numpy as np

# Import sounddevice to play audio
import sounddevice as sd

# Import tkinter for GUI development
import tkinter as tk

# Import messagebox from tkinter for popup messages
from tkinter import messagebox

# Import QTM SDK module to communicate with Qualisys
import qtm

# Import os to interact with the operating system
import os

# Change current working directory (may be necessary for saving or accessing files)
os.chdir("C:/Users/Ricki")

# Declare a global variable to hold the QTM connection
qtm_connection = None

# Asynchronous function to connect and start recording in QTM
async def start_qtm_recording():
    global qtm_connection
    try:
        # Connect to QTM server at localhost
        qtm_connection = await qtm.connect("127.0.0.1")
        print("Connected to QTM.")

        # Take control of QTM (no password provided)
        await qtm_connection.take_control("")

        # Start the recording session
        await qtm_connection.start()
        print("Recording started.")

    except Exception as e:
        # Handle connection or control errors
        print(f"Failed to start QTM recording: {e}")
        qtm_connection = None

# Synchronous function to play a beep sound (blocks execution while sound plays)
def play_beep_blocking():
    fs = 44100  # Audio sampling rate in Hz
    duration = 0.5  # Duration of the beep in seconds
    frequency = 500  # Frequency of the beep in Hz

    # Create a time array for the sound wave
    t = np.linspace(0, duration, int(fs * duration), False)
    
    # Generate a sine wave at the specified frequency
    beep = 0.5 * np.sin(2 * np.pi * frequency * t)

    # Play the beep sound
    sd.play(beep, fs)
    
    # Wait until the sound has finished playing
    sd.wait()

# Asynchronous function to start QTM recording and play a beep after a short delay
async def start_recording_and_beep():
    # Start QTM recording
    await start_qtm_recording()
    
    # If connection failed, show an error message in the GUI
    if qtm_connection is None:
        def show_error():
            messagebox.showerror("Error", "Failed to start recording.")
        root.after(0, show_error)
        return

    # Wait for 0.5 seconds before playing the beep
    await asyncio.sleep(0.5)

    # Play beep sound in a separate thread to avoid blocking the event loop
    await asyncio.to_thread(play_beep_blocking)

    # Do not stop recording here—stop is handled by the Stop button

# Function triggered when "Start Recording" button is pressed
def on_start_button():
    def runner():
        # Run the asynchronous start+beep sequence in a new thread
        asyncio.run(start_recording_and_beep())
    
    # Start the thread as a daemon so it ends with the main program
    threading.Thread(target=runner, daemon=True).start()

# Function triggered when "Stop Recording" button is pressed
def on_stop_button():
    def runner():
        # Run the asynchronous stop function in a new thread
        asyncio.run(stop_recording())
    
    # Start the thread as a daemon
    threading.Thread(target=runner, daemon=True).start()

# Asynchronous function to stop recording and disconnect from QTM
async def stop_recording():
    global qtm_connection
    if qtm_connection:
        try:
            # Stop the QTM recording
            await qtm_connection.stop()
            print("Recording stopped.")
            
            # Disconnect from QTM
            qtm_connection.disconnect()
            print("Disconnected from QTM.")
            qtm_connection = None
        except Exception as e:
            # Handle any errors during stopping or disconnecting
            print(f"Failed to stop QTM recording: {e}")
            def show_error():
                messagebox.showerror("Error", "Failed to stop recording.")
            root.after(0, show_error)
    else:
        # No active connection to stop
        print("No active connection to stop.")

# Function to build and run the GUI
def build_gui():
    global root

    # Create main application window
    root = tk.Tk()
    root.title("QTM Controller")

    # Create "Start Recording" button and place it in the window
    start_btn = tk.Button(root, text="Start Recording", command=on_start_button, width=25, height=3)
    start_btn.pack(pady=10, padx=20)

    # Create "Stop Recording" button and place it below the start button
    stop_btn = tk.Button(root, text="Stop Recording", command=on_stop_button, width=25, height=3)
    stop_btn.pack(pady=10, padx=20)

    # Start the GUI event loop
    root.mainloop()

# Run the application if this script is executed directly
if __name__ == "__main__":
    build_gui()
