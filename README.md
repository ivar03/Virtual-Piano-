# Virtual Piano with Dual Camera Hand Tracking

A computer vision-based virtual piano system that uses two cameras to detect and track hand movements for playing a MIDI piano. The system combines top-view finger position detection with front-view depth tracking to create a more accurate and immersive virtual piano experience.

## Overview

This project implements a virtual piano interface that allows users to play piano notes using hand gestures captured by two cameras. The system uses:
- A top camera to track finger positions over piano keys
- A front camera to detect key press depth
- MIDI output for realistic piano sounds
- Hand tracking using MediaPipe (to be replaced with custom model in future)

## Features

- Real-time hand and finger tracking
- 88-key piano support (Full piano range from A0 to C8)
- Visual feedback for:
  - Piano key layout
  - Finger positions
  - Key press detection
  - Black and white key differentiation
- MIDI sound output with velocity sensitivity
- Support for multiple fingers and both hands simultaneously

## Requirements

```
python >= 3.8
opencv-python
mediapipe
pygame
numpy
```

You'll also need:
- Two webcams (one for top view, one for front view)
- MIDI soundfont (.sf2 file)
- Compatible MIDI output device/driver

## Setup

1. Install required packages:
```bash
pip install opencv-python mediapipe pygame numpy
```

2. Connect two cameras to your system

3. Configure camera indices in the code (default: 0 for top camera, 1 for front camera)

4. Run the application:
```bash
python virtual_piano.py
```

## Usage

1. Position the cameras:
   - Top camera should view the piano area from above
   - Front camera should view from the front to detect key press depth

2. Adjust the key press threshold if needed (default is 60% of frame height)

3. Play notes by:
   - Moving fingers over desired keys (top view)
   - Pressing down below the threshold line (front view)

4. Press 'q' to quit the application

## Known Issues and Future Improvements

1. Hand Tracking Limitations:
   - Current MediaPipe implementation has occasional tracking issues
   - Planning to replace with custom hand tracking model
   - Need to improve finger ID correlation between cameras

2. Performance Optimizations:
   - Real-time processing can be improved
   - Need to reduce latency in MIDI output

3. Calibration:
   - Add camera calibration system
   - Implement automatic threshold adjustment
   - Add key width calibration

4. Features to Add:
   - Sustain pedal support
   - Velocity sensitivity based on press depth
   - Multiple sound font support
   - Recording functionality

---
**Note:** This is an ongoing project, and the hand tracking system will be updated with a custom model in future releases for improved accuracy and performance.
