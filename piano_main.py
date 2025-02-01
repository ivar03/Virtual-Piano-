import cv2
import numpy as np
import mediapipe as mp
import pygame
import pygame.midi
from collections import defaultdict

class PianoDetectionSystem:
    def __init__(self):
        # Initialize MediaPipe for both cameras
        self.mp_hands = mp.solutions.hands
        self.hands_top = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.hands_front = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Initialize pygame and MIDI
        pygame.init()
        pygame.midi.init()
        self.midi_device_id = pygame.midi.get_default_output_id()
        self.midi_output = pygame.midi.Output(self.midi_device_id)
        self.midi_output.set_instrument(0)

        # Camera settings
        self.width = 1280
        self.height = 720
        self.setup_cameras()

        # Piano configuration
        self.num_lines = 53
        self.spacing = self.width // self.num_lines
        self.indices = [1, 5, 7, 11, 13, 15, 19, 21, 25, 27, 29, 33, 35, 39, 41, 43, 47, 49, 
                       53, 55, 57, 61, 63, 67, 69, 71, 75, 77, 81, 83, 85, 89, 91, 95, 97, 99]
        self.white_indices = [1, 3, 4, 6, 7, 8, 10, 11, 13, 14, 15, 17, 18, 20, 21, 22, 24, 25, 
                            27, 28, 29, 31, 32, 34, 35, 36, 38, 39, 41, 42, 43, 45, 46, 48, 49, 50]

        # State tracking
        self.currently_playing = defaultdict(set)
        self.finger_positions_top = {}  # Track finger positions from top view
        self.finger_positions_front = {}  # Track finger positions from front view
        self.key_press_threshold = int(self.height * 0.6)

    def setup_cameras(self):
        self.cap_top = cv2.VideoCapture(1)
        self.cap_front = cv2.VideoCapture(0)
        for cap in [self.cap_top, self.cap_front]:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def draw_rectangles(self, frame):
        black_rects = []
        for index in self.indices:
            rect_x = index * (self.spacing // 2)
            rect_top_left = (rect_x, 480)
            rect_bottom_right = (rect_x + self.spacing, 620)
            black_rects.append((rect_top_left, rect_bottom_right))
            cv2.rectangle(frame, rect_top_left, rect_bottom_right, (0, 0, 0), 1)
        return black_rects

    def get_note_from_position(self, x):
        key_index = int(x // self.spacing) + 21  # Start from A0 (21)
        if 21 <= key_index <= 108:  # Valid note range
            return key_index
        return None

    def play_note(self, note, finger_id):
        if note and note not in self.currently_playing[finger_id]:
            velocity = 127  # Maximum velocity
            self.midi_output.note_on(note, velocity)
            self.currently_playing[finger_id].add(note)
            print(f"Playing note: {note}")

    def stop_note(self, note, finger_id):
        if note in self.currently_playing[finger_id]:
            self.midi_output.note_off(note, velocity=0)
            self.currently_playing[finger_id].remove(note)

    def process_hands(self, frame, hands_detector, is_front_view=False):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands_detector.process(rgb_frame)
        
        finger_positions = {}
        
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                for finger_id, tip_id in enumerate([4, 8, 12, 16, 20]):
                    x = int(hand_landmarks.landmark[tip_id].x * self.width)
                    y = int(hand_landmarks.landmark[tip_id].y * self.height)
                    
                    # Create unique finger ID combining hand index and finger index
                    unique_finger_id = f"{hand_idx}_{finger_id}"
                    finger_positions[unique_finger_id] = (x, y)
                    
                    # Draw finger position
                    color = (0, 255, 0) if not is_front_view else (0, 0, 255)
                    cv2.circle(frame, (x, y), 10, color, -1)

        return frame, finger_positions

    def process_top_view(self, frame):
        # Draw piano keys
        for i in range(1, self.num_lines):
            x = i * self.spacing
            if i in self.white_indices:
                cv2.line(frame, (x, 620), (x, self.height), (255, 255, 255), 1)
            else:
                cv2.line(frame, (x, 480), (x, self.height), (255, 255, 255), 1)

        # Add overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, 480), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.75, frame, 0.25, 0)

        # Draw black keys
        self.draw_rectangles(frame)

        # Process hand landmarks
        frame, self.finger_positions_top = self.process_hands(frame, self.hands_top)
        return frame

    def process_front_view(self, frame):
        # Draw vertical lines and threshold
        for i in range(1, self.num_lines):
            x = i * self.spacing
            cv2.line(frame, (x, 0), (x, self.height), (255, 255, 255), 1)
        
        cv2.line(frame, (0, self.key_press_threshold), 
                (self.width, self.key_press_threshold), (0, 255, 0), 2)

        # Process hand landmarks
        frame, self.finger_positions_front = self.process_hands(frame, self.hands_front, True)
        return frame

    def update_notes(self):
        # Clear current notes
        active_notes = set()

        # Check each finger from top view
        for finger_id, (x, y) in self.finger_positions_top.items():
            if 480 <= y <= self.height:  # Finger is in piano key area
                note = self.get_note_from_position(x)
                
                # Check if corresponding finger in front view is below threshold
                if finger_id in self.finger_positions_front:
                    front_x, front_y = self.finger_positions_front[finger_id]
                    if front_y > self.key_press_threshold:
                        self.play_note(note, finger_id)
                        active_notes.add(finger_id)

        # Stop notes for inactive fingers
        for finger_id in list(self.currently_playing.keys()):
            if finger_id not in active_notes:
                for note in list(self.currently_playing[finger_id]):
                    self.stop_note(note, finger_id)

    def run(self):
        try:
            while True:
                ret_top, frame_top = self.cap_top.read()
                ret_front, frame_front = self.cap_front.read()

                if not ret_top or not ret_front:
                    print("Failed to capture frames")
                    break

                frame_top = cv2.resize(frame_top, (self.width, self.height))
                frame_front = cv2.resize(frame_front, (self.width, self.height))
                #frame_top = cv2.flip(frame_top, 1)
                frame_front = cv2.flip(frame_front, 1)

                processed_top = self.process_top_view(frame_top)
                processed_front = self.process_front_view(frame_front)
                
                # Update note playing based on both camera inputs
                self.update_notes()

                cv2.imshow("Top View", processed_top)
                cv2.imshow("Front View", processed_front)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            self.cleanup()

    def cleanup(self):
        # Stop all playing notes
        for finger_id in self.currently_playing:
            for note in list(self.currently_playing[finger_id]):
                self.stop_note(note, finger_id)

        self.cap_top.release()
        self.cap_front.release()
        cv2.destroyAllWindows()
        self.midi_output.close()
        pygame.midi.quit()
        pygame.quit()

if __name__ == "__main__":
    piano_system = PianoDetectionSystem()
    piano_system.run()