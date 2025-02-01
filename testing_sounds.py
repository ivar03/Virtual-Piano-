import pygame
import pygame.midi
from pynput.keyboard import Listener

# Initialize pygame and pygame.midi
pygame.init()
pygame.midi.init()

# Load your SoundFont (.sf2) file
soundfont_path = 'Arnold___David_Classical_Piano.sf2'  # Replace with your actual .sf2 file path
midi_device_id = pygame.midi.get_default_output_id()  # Default MIDI device

# Open the MIDI output device
midi_output = pygame.midi.Output(midi_device_id)
midi_output.set_instrument(0)  # Select an instrument (0 is the default piano)

# Define the piano key mappings to MIDI note numbers
key_mapping = {
    'q': 60,  # C (Middle C)
    'w': 61,  # C#
    'e': 62,  # D
    'r': 63,  # D#
    't': 64,  # E
    'y': 65,  # F
    'u': 66,  # F#
    'i': 67,  # G
    'o': 68,  # G#
    'p': 69,  # A
    'a': 70,  # A#
    's': 71,  # B
    'd': 72,  # C (Octave 2)
    'f': 73,  # C#
    'g': 74,  # D
    'h': 75,  # D#
    'j': 76,  # E
    'k': 77,  # F
    'l': 78,  # F#
    'z': 79,  # G
    'x': 80,  # G#
    'c': 81,  # A
    'v': 82,  # A#
    'b': 83,  # B
    'n': 84,  # C (Octave 3)
    'm': 85   # C#
}

# Function to play sound when a key is pressed
def play_note(note):
    midi_output.note_on(note, velocity=127)  # 127 is max velocity (loudest)

# Function to stop sound when a key is released
def stop_note(note):
    midi_output.note_off(note, velocity=127)

# Function to handle key press events
def on_press(key):
    try:
        if hasattr(key, 'char') and key.char in key_mapping:
            note = key_mapping[key.char]
            print(f"Playing note: {note}")
            play_note(note)
    except AttributeError:
        pass

# Function to handle key release events
def on_release(key):
    try:
        if hasattr(key, 'char') and key.char in key_mapping:
            note = key_mapping[key.char]
            stop_note(note)
    except AttributeError:
        pass

    if key == 'esc':  # Press 'esc' to stop the listener
        return False

# Start listening for key presses
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# Close the MIDI output after finishing
midi_output.close()
pygame.midi.quit()
pygame.quit()
