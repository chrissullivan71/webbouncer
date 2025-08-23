import pygame
import time
import re
import pprint
import threading
import pyaudio
import wave
from datetime import datetime
from typing import List, Dict, Tuple

"""
High Flight Teleprompter 
Copyright (c) 2025 Chris Sullivan. All rights reserved.
"""

# High Flight poem - clean text only
HIGH_FLIGHT_LINES = [
    "Oh! I have slipped the surly bonds of Earth",
    "And danced the skies on laughter-silvered wings;",
    "Sunward I've climbed, and joined the tumbling mirth",
    "of sun-split clouds, — and done a hundred things",
    "You have not dreamed of – wheeled and soared and swung",
    "High in the sunlit silence. Hov'ring there,",
    "I've chased the shouting wind along, and flung",
    "My eager craft through footless halls of air....",
    "",
    "Up, up the long, delirious, burning blue",
    "I've topped the wind-swept heights with easy grace.",
    "Where never lark, or even eagle flew —",
    "And, while with silent, lifting mind I've trod",
    "The high untrespassed sanctity of space,",
    "Put out my hand, and touched the face of God."
]

def interpolate_color(color1, color2, factor):
    """Interpolate between two colors. factor 0=color1, factor 1=color2"""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    return (r, g, b)

# Button functions to replace Button class
def draw_button(screen, rect, text, font, is_hovered=False, is_pressed=False, color=(0, 102, 204), text_color=(255, 255, 255)):
    """Draw a button with text"""
    hover_color = (0, 128, 255)
    press_color = (0, 80, 160)
    
    if is_pressed:
        button_color = press_color
    elif is_hovered:
        button_color = hover_color
    else:
        button_color = color
    
    pygame.draw.rect(screen, button_color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def is_button_clicked(rect, event):
    """Check if button was clicked"""
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1 and rect.collidepoint(event.pos):
            return True
    return False

def is_button_hovered(rect, mouse_pos):
    """Check if mouse is hovering over button"""
    return rect.collidepoint(mouse_pos)

# Speed slider functions to replace SpeedSlider class
def draw_speed_slider(screen, rect, font, values, labels, current_index, label_text="Speed"):
    """Draw speed slider"""
    knob_radius = 10
    
    # Draw slider track
    track_rect = pygame.Rect(rect.x, rect.centery - 2, rect.width, 4)
    pygame.draw.rect(screen, (100, 100, 100), track_rect)
    
    # Draw position markers
    for i in range(len(values)):
        marker_x = rect.x + (i / (len(values) - 1)) * rect.width
        pygame.draw.circle(screen, (150, 150, 150), (int(marker_x), rect.centery), 3)
    
    # Draw knob
    knob_x = rect.x + (current_index / (len(values) - 1)) * rect.width
    pygame.draw.circle(screen, (255, 255, 255), (int(knob_x), rect.centery), knob_radius)
    pygame.draw.circle(screen, (0, 102, 204), (int(knob_x), rect.centery), knob_radius - 2)
    
    # Draw label
    current_label = labels[current_index]
    label_surface = font.render(f"{label_text}: {current_label}", True, (255, 255, 255))
    label_rect = label_surface.get_rect(center=(rect.centerx, rect.y - 15))
    screen.blit(label_surface, label_rect)

def handle_speed_slider(rect, values, current_index, event, dragging):
    """Handle speed slider events, returns (new_index, new_dragging_state, changed)"""
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1 and rect.collidepoint(event.pos):
            dragging = True
            new_index, changed = update_slider_from_mouse(rect, values, current_index, event.pos)
            return new_index, dragging, changed
    elif event.type == pygame.MOUSEBUTTONUP:
        dragging = False
    elif event.type == pygame.MOUSEMOTION and dragging:
        new_index, changed = update_slider_from_mouse(rect, values, current_index, event.pos)
        return new_index, dragging, changed
    
    return current_index, dragging, False

def update_slider_from_mouse(rect, values, current_index, pos):
    """Update slider position from mouse, returns (new_index, changed)"""
    relative_x = pos[0] - rect.x
    progress = max(0, min(1, relative_x / rect.width))
    new_index = round(progress * (len(values) - 1))
    
    changed = (new_index != current_index)
    return new_index, changed

# Button outline functions for controls image
def scale_button_coordinates(original_coords, original_image_size, scaled_image_size):
    """Scale button coordinates from original image size to scaled size"""
    orig_width, orig_height = original_image_size
    scaled_width, scaled_height = scaled_image_size
    
    scale_x = scaled_width / orig_width
    scale_y = scaled_height / orig_height
    
    scaled_coords = []
    for x, y in original_coords:
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        scaled_coords.append((scaled_x, scaled_y))
    
    return scaled_coords

def offset_coordinates(coords, offset_x, offset_y):
    """Offset coordinates by the given x,y amounts"""
    return [(x + offset_x, y + offset_y) for x, y in coords]

def draw_button_outline(screen, coords, color=(0, 255, 0), width=2):
    """Draw polygon outline for button region"""
    if len(coords) >= 3:
        pygame.draw.polygon(screen, color, coords, width)

def point_in_polygon(point, polygon):
    """Check if point is inside polygon using ray casting algorithm"""
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def check_button_click(mouse_pos, button_coords):
    """Check which button was clicked, returns button name or None"""
    for button_name, coords in button_coords.items():
        if point_in_polygon(mouse_pos, coords):
            return button_name
    return None

# Audio recording variables
is_recording = False
recording_thread = None
audio_frames = []
audio_stream = None
p_audio = None

# Playback mode variables
playback_mode = "normal"  # "normal", "playback_idle", "playback_active"
audio_file = None
audio_position = 0.0

# Audio recording functions
def start_recording():
    """Start audio recording in a separate thread"""
    global is_recording, recording_thread, audio_frames, audio_stream, p_audio
    
    if is_recording:
        return
    
    try:
        # Initialize pyaudio
        p_audio = pyaudio.PyAudio()
        
        # Audio settings
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1  # Mono
        fs = 44100  # Sample rate
        
        # Start recording stream
        audio_stream = p_audio.open(format=sample_format,
                                   channels=channels,
                                   rate=fs,
                                   frames_per_buffer=chunk,
                                   input=True)
        
        audio_frames = []
        is_recording = True
        
        # Start recording thread
        recording_thread = threading.Thread(target=record_audio_worker, args=(audio_stream, chunk))
        recording_thread.daemon = True
        recording_thread.start()
        
        print("🎙️ Recording started...")
        
    except Exception as e:
        print(f"Error starting recording: {e}")
        is_recording = False

def record_audio_worker(stream, chunk):
    """Worker function for recording audio in background thread"""
    global is_recording, audio_frames
    
    while is_recording:
        try:
            data = stream.read(chunk, exception_on_overflow=False)
            audio_frames.append(data)
        except Exception as e:
            print(f"Recording error: {e}")
            break

def stop_recording():
    """Stop audio recording and save file"""
    global is_recording, recording_thread, audio_frames, audio_stream, p_audio
    
    if not is_recording:
        return
    
    is_recording = False
    
    try:
        # Wait for recording thread to finish
        if recording_thread:
            recording_thread.join(timeout=1.0)
        
        # Stop and close the stream
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
        
        # Terminate pyaudio
        if p_audio:
            p_audio.terminate()
        
        # Save the recording
        if audio_frames:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"recording_{timestamp}.wav"
            
            # Write WAV file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(p_audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(audio_frames))
            wf.close()
            
            print(f"🎵 Recording saved: {filename}")
        
        # Reset variables
        audio_frames = []
        audio_stream = None
        p_audio = None
        recording_thread = None
        
    except Exception as e:
        print(f"Error stopping recording: {e}")

def toggle_recording():
    """Toggle recording on/off"""
    if is_recording:
        stop_recording()
    else:
        start_recording()

# Initialize pygame first
pygame.init()

# Screen setup
clock = pygame.time.Clock()
screen_width = 1920
screen_height = 1020
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption("High Flight Teleprompter")

# Font setup
title_font = pygame.font.SysFont("Courier", 40, bold=True)
poem_font = pygame.font.SysFont("Arial", 48, bold=False)  # Large poem font
button_font = pygame.font.SysFont("Courier", 24, bold=True)
small_font = pygame.font.SysFont("Courier", 18)

# Create UI buttons and controls
button_x = screen_width - 180
play_pause_rect = pygame.Rect(button_x, 80, 160, 40)
restart_rect = pygame.Rect(button_x, 130, 160, 40)

# Button state variables
play_pause_hovered = False
play_pause_pressed = False
restart_hovered = False
restart_pressed = False

# Speed slider variables
speed_rect = pygame.Rect(button_x, 300, 160, 20)
speed_values = [1.0, 1.25, 1.5, 1.75, 2.0]
speed_labels = ["1.0x", "1.25x", "1.5x", "1.75x", "2.0x"]
speed_current_index = 0
speed_dragging = False

# Original controls image coordinates (2040 x 3708 pixels)
ORIGINAL_CONTROLS_SIZE = (2040, 3708)

# Button coordinates from original image
button_coords_original = {
    "playback_mode": [(200, 50), (1800, 50), (1800, 200), (200, 200)],  # Top of controls image
    "forward": [(63, 1953), (1866, 1851), (1888, 2048), (79, 2166)],
    "fast_rewind": [(162, 1242), (1011, 1207), (1038, 1411), (189, 1455)],
    "fast_forward": [(1216, 1216), (1987, 1194), (2010, 1393), (1251, 1413)],
    "pause": [(1170, 2632), (1944, 2563), (1966, 2766), (1197, 2844)],
    "stop_eject": [(154, 3454), (1934, 3229), (1956, 3434), (176, 3666)],
    "record": [(136, 2702), (976, 2619), (1002, 2844), (124, 2929)]
}

BACKGROUND_FILE = r"assets\background.jpg"
CONTROLS_FILE = r"assets\controls.jpg"
MAG_TAPE_FILE = r"assets\magtape.jpg"
ICON_FILE = r"assets\icon.png"

# Load icon
try:
    icon = pygame.image.load(ICON_FILE)
    pygame.display.set_icon(icon)
except FileNotFoundError:
    pass  # Icon not critical

# Load background image
try:
    background_image = pygame.image.load(BACKGROUND_FILE)
    background_image = pygame.transform.scale(background_image, screen.get_size())
except FileNotFoundError:
    print(f"Background image not found: {BACKGROUND_FILE}")
    background_image = None

# Load controls image (bottom left)
try:
    controls_image = pygame.image.load(CONTROLS_FILE)
    controls_height = screen.get_height() // 3 + 72
    controls_width = int(controls_image.get_width() * controls_height / controls_image.get_height())
    controls_image = pygame.transform.scale(controls_image, (controls_width, controls_height))
    controls_image_size = (controls_width, controls_height)
except FileNotFoundError:
    print(f"Controls image not found: {CONTROLS_FILE}")
    controls_image = None
    controls_image_size = (0, 0)

# Load mag tape image (top, full width)
try:
    mag_tape_image = pygame.image.load(MAG_TAPE_FILE)
    tape_height = screen.get_height() // 8
    mag_tape_image = pygame.transform.scale(mag_tape_image, (screen.get_width(), tape_height))
except FileNotFoundError:
    print(f"Mag tape image not found: {MAG_TAPE_FILE}")
    mag_tape_image = None

# Calculate scaled button coordinates for controls image
scaled_button_coords = {}
if controls_image:
    controls_x = 20
    controls_y = screen.get_height() - controls_height - 20
    
    for button_name, coords in button_coords_original.items():
        # Scale coordinates to match the scaled controls image
        scaled_coords = scale_button_coordinates(coords, ORIGINAL_CONTROLS_SIZE, controls_image_size)
        # Offset by the controls image position on screen
        final_coords = offset_coordinates(scaled_coords, controls_x, controls_y)
        scaled_button_coords[button_name] = final_coords

# Y position constants
POSITION_TITLE = 120
POSITION_TIME_SIGNATURE = 150

# Scrolling variables
scroll_offset = 0.0
base_scroll_speed = 10.0  # pixels per second (reduced from 30 for slower reading pace)
last_time = time.time()

current_line = 0
waiting_for_start = True
song_paused = False

# Main game loop
running = True

while running:
    current_time = time.time()
    
    # Update scrolling
    if playback_mode == "normal":
        # Normal time-based scrolling
        if not waiting_for_start and not song_paused:
            dt = current_time - last_time
            current_speed = base_scroll_speed * speed_values[speed_current_index]
            scroll_offset += current_speed * dt
    else:
        # Playback mode - sync with audio position
        if playback_mode == "playback_active":
            # TODO: Calculate scroll_offset based on audio_position
            # For now, use time-based scrolling in playback mode too
            if not waiting_for_start and not song_paused:
                dt = current_time - last_time
                current_speed = base_scroll_speed * speed_values[speed_current_index]
                scroll_offset += current_speed * dt
    
    last_time = current_time

    # Draw background
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((30, 30, 30))

    # Draw mag tape at top
    if mag_tape_image:
        screen.blit(mag_tape_image, (0, 0))

        # Draw position indicator (static for now)
        indicator_width = 8
        position_x = 50  # Static position
        indicator_height = mag_tape_image.get_height() // 2
        indicator_y = mag_tape_image.get_height() // 4

        rect_x = position_x - indicator_width // 2
        rect_x = max(0, min(rect_x, screen.get_width() - indicator_width))

        pygame.draw.rect(screen, (0, 255, 0),
                         (rect_x, indicator_y, indicator_width, indicator_height))

        circle_center_x = rect_x + indicator_width // 2
        circle_center_y = indicator_y + indicator_height // 2
        circle_radius = 5
        pygame.draw.circle(screen, (255, 255, 255), (circle_center_x, circle_center_y), circle_radius)

    # Draw controls at bottom left and button outlines
    if controls_image:
        controls_y = screen.get_height() - controls_image.get_height() - 20
        controls_x = 20
        screen.blit(controls_image, (controls_x, controls_y))

        # Draw button outlines and fill playback mode button
        for button_name, coords in scaled_button_coords.items():
            if button_name == "playback_mode":
                # Mode button: Green (normal), Yellow (idle), Red (active) - FILLED
                if playback_mode == "normal":
                    color = (0, 255, 0)      # Green for normal mode
                elif playback_mode == "playback_idle":
                    color = (255, 255, 0)    # Yellow for playback idle
                else:  # playback_active
                    color = (255, 0, 0)      # Red for playing back
                
                # Draw filled rectangle for mode button
                pygame.draw.polygon(screen, color, coords)
                # Add black outline
                pygame.draw.polygon(screen, (0, 0, 0), coords, 2)
                
            else:
                # All other buttons remain outlines
                if button_name == "forward":
                    color = (0, 255, 0)      # Green for play
                elif button_name == "pause":
                    color = (255, 255, 0)    # Yellow for pause
                elif button_name == "stop_eject":
                    color = (255, 0, 0)      # Red for stop
                elif button_name == "fast_rewind":
                    color = (0, 150, 255)    # Light blue for rewind
                elif button_name == "fast_forward":
                    color = (0, 150, 255)    # Light blue for fast forward
                elif button_name == "record":
                    if playback_mode != "normal":
                        color = (100, 100, 100)  # Grey when in playback mode
                    else:
                        color = (255, 50, 50) if is_recording else (0, 255, 0)  # Bright red when recording, green when not
                else:
                    color = (255, 255, 255)  # White default
                
                draw_button_outline(screen, coords, color, 4 if (button_name == "record" and is_recording) else 3)

    # Always display title
    title_text = "High Flight - by John Gillespie Magee Jr."
    title_surface = title_font.render(title_text, True, (0, 255, 0))
    screen.blit(title_surface, (50, POSITION_TITLE))

    # Measure all poem lines to find maximum width and height for window sizing
    max_width = 0
    max_height = 0
    for line in HIGH_FLIGHT_LINES:
        if line.strip():  # Don't measure empty lines
            line_surface = poem_font.render(line, True, (255, 255, 255))
            max_width = max(max_width, line_surface.get_width())
            max_height = max(max_height, line_surface.get_height())
    
    # Draw blue window frame in center of screen - sized to fit largest line
    line_height = 60
    window_width = int(max_width * 1.15)  # 15% bigger than longest line
    window_height = int(max_height * 1.15)  # 15% bigger than tallest line
    window_x = (screen_width - window_width) // 2
    window_y = (screen_height - window_height) // 2
    window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
    
    # Draw blue square outline (not filled)
    pygame.draw.rect(screen, (100, 100, 255), window_rect, 4)  # 4 pixel border
    
    # Display poem text with smooth scrolling - simple white text
    line_height = 60
    # Start text so first line is about half a line below the blue square
    base_start_y = window_y + window_height + (line_height // 2)
    start_y = base_start_y - scroll_offset
    
    # Render all text in white (no clipping needed)
    for i, line in enumerate(HIGH_FLIGHT_LINES):
        if line.strip():  # Don't render empty lines
            line_surface = poem_font.render(line, True, (255, 255, 255))
            line_x = (screen_width - line_surface.get_width()) // 2  # Center text
            line_y = start_y + i * line_height
            # Only draw if line is visible on screen
            if line_y > -line_height and line_y < screen_height:
                screen.blit(line_surface, (line_x, line_y))

    # Calculate current line in reading box for display
    reading_box_center_y = window_y + window_height // 2
    current_poem_line = 0
    
    # Find which poem line is closest to the reading box center
    min_distance = float('inf')
    for i, line in enumerate(HIGH_FLIGHT_LINES):
        if line.strip():  # Only count non-empty lines
            line_y = start_y + i * line_height
            line_center_y = line_y + line_height // 2
            distance = abs(line_center_y - reading_box_center_y)
            if distance < min_distance:
                min_distance = distance
                current_poem_line = i + 1  # 1-based line numbering

    # Show recording indicator, playback mode, and line number
    if is_recording:
        rec_font = pygame.font.SysFont("Courier", 24, bold=True)
        rec_surface = rec_font.render("● REC", True, (255, 50, 50))
        screen.blit(rec_surface, (screen_width - 120, 50))
    
    # Show current line number
    line_font = pygame.font.SysFont("Courier", 20, bold=True)
    line_surface = line_font.render(f"Line: {current_poem_line}/{len([l for l in HIGH_FLIGHT_LINES if l.strip()])}", True, (255, 255, 255))
    screen.blit(line_surface, (screen_width - 120, 20))
    
    # Show playback mode status
    if playback_mode != "normal":
        mode_font = pygame.font.SysFont("Courier", 20, bold=True)
        mode_text = "PLAYBACK IDLE" if playback_mode == "playback_idle" else "PLAYBACK ACTIVE"
        mode_color = (255, 255, 0) if playback_mode == "playback_idle" else (255, 100, 100)
        mode_surface = mode_font.render(mode_text, True, mode_color)
        screen.blit(mode_surface, (screen_width - 200, 80))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break
            elif event.key == pygame.K_q:
                # Q quits the game
                running = False
                break
            elif event.key == pygame.K_SPACE:
                if waiting_for_start:
                    waiting_for_start = False
                elif song_paused:
                    song_paused = False
                else:
                    song_paused = True
            elif event.key == pygame.K_r:
                current_line = 0
                waiting_for_start = True
                song_paused = False
                scroll_offset = 0.0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check for button clicks on controls image
            if event.button == 1 and scaled_button_coords:
                clicked_button = check_button_click(event.pos, scaled_button_coords)
                if clicked_button:
                    print(f"Button clicked: {clicked_button}")
                    
                    if clicked_button == "playback_mode":
                        # Cycle through playback modes
                        if playback_mode == "normal":
                            playback_mode = "playback_idle"
                            print("Switched to playback mode (idle)")
                        elif playback_mode == "playback_idle":
                            playback_mode = "playback_active"  
                            print("Started audio playback")
                            # TODO: Start audio playback here
                        else:  # playback_active
                            playback_mode = "normal"
                            print("Stopped playback, returned to normal mode")
                            # TODO: Stop audio playback here
                    
                    elif clicked_button == "forward":
                        if playback_mode == "normal":
                            # Normal text scrolling mode
                            if waiting_for_start:
                                waiting_for_start = False
                            elif song_paused:
                                song_paused = False
                            else:
                                song_paused = True
                        else:
                            # Playback mode - control audio
                            if playback_mode == "playback_idle":
                                playback_mode = "playback_active"
                                print("Started audio playback")
                            elif playback_mode == "playback_active":
                                playback_mode = "playback_idle"
                                print("Paused audio playback")
                    
                    elif clicked_button == "pause":
                        if playback_mode == "normal":
                            # Normal mode - pause/unpause text only
                            if not waiting_for_start:
                                if song_paused:
                                    song_paused = False
                                else:
                                    song_paused = True
                        else:
                            # Playback mode - pause audio
                            if playback_mode == "playback_active":
                                playback_mode = "playback_idle"
                                print("Paused audio playback")
                    
                    elif clicked_button == "stop_eject":
                        # Stop everything and restart
                        if playback_mode != "normal":
                            playback_mode = "playback_idle"
                            print("Stopped audio playback")
                        current_line = 0
                        waiting_for_start = True
                        song_paused = False
                        scroll_offset = 0.0
                    
                    elif clicked_button == "record":
                        # Only allow recording in normal mode
                        if playback_mode == "normal":
                            toggle_recording()
                        else:
                            print("Recording disabled during playback mode")

        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        play_pause_hovered = is_button_hovered(play_pause_rect, mouse_pos)
        restart_hovered = is_button_hovered(restart_rect, mouse_pos)

        # Handle button events
        if is_button_clicked(play_pause_rect, event):
            # Same logic as spacebar
            if waiting_for_start:
                waiting_for_start = False
            elif song_paused:
                song_paused = False
            else:
                song_paused = True

        if is_button_clicked(restart_rect, event):
            # Same logic as 'R' key
            current_line = 0
            waiting_for_start = True
            song_paused = False
            scroll_offset = 0.0

        # Handle speed slider
        speed_current_index, speed_dragging, speed_changed = handle_speed_slider(
            speed_rect, speed_values, speed_current_index, event, speed_dragging
        )

    # Draw UI buttons and controls
    play_text = "Pause" if not waiting_for_start and not song_paused else "Play"
    draw_button(screen, play_pause_rect, play_text, button_font, play_pause_hovered, play_pause_pressed)
    draw_button(screen, restart_rect, "Restart", button_font, restart_hovered, restart_pressed)
    draw_speed_slider(screen, speed_rect, small_font, speed_values, speed_labels, speed_current_index)

    # Draw controls help text - start about 1 inch below title line
    help_start_y = POSITION_TITLE + 96  # About 1 inch below title (96 pixels)
    help_lines = [
        "KEYBOARD:",
        "Space: Play/Pause",
        "R: Restart, Q/Esc: Quit"
    ]

    # Use button_font for readability - draw wrapped help text
    for i, help_line in enumerate(help_lines):
        help_surface = button_font.render(help_line, True, (255, 255, 255))
        screen.blit(help_surface, (50, help_start_y + i * 28))

    pygame.display.flip()
    clock.tick(60)

# Cleanup recording if still active
if is_recording:
    stop_recording()

pygame.quit()
