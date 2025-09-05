import pygame
import time
import re
import pprint
import string
from typing import List, Dict, Tuple

"""
Bouncing Ball Teleprompter (BBT)
Copyright (c) 2025 Chris Sullivan. All rights reserved.
"""

def interpolate_color(color1, color2, factor):
    """Interpolate between two colors. factor 0=color1, factor 1=color2"""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    return (r, g, b)

def parse_time_signature(time_sig_string):
    """Parse time signature from string like '3/4' or '4/4'"""
    try:
        if "/" in time_sig_string:
            parts = time_sig_string.strip().split("/")
            numerator = int(parts[0])
            denominator = int(parts[1])
            return numerator, denominator
        else:
            # Try to extract just numbers
            numbers = re.findall(r'\d+', time_sig_string)
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
    except (ValueError, IndexError):
        print(f"Could not parse time signature: {time_sig_string}, using 4/4")
    
    return 4, 4  # default fallback
    
def render_text_line(text, font, x_pos, y_pos, default_color, highlight_words=None):
    """Render a line of text with optional word highlighting"""
    words = text.split()
    current_x = x_pos
    
    for word in words:
        if highlight_words and word in highlight_words:
            color = highlight_words[word]
        else:
            color = default_color
            
        word_surface = font.render(word, True, color)
        screen.blit(word_surface, (current_x, y_pos))
        current_x += word_surface.get_width() + font.size(' ')[0]    

def create_button(x, y, width, height, text, font, color=(0, 102, 204), text_color=(255, 255, 255)):
    """Create a button dictionary"""
    return {
        'rect': pygame.Rect(x, y, width, height),
        'text': text,
        'font': font,
        'color': color,
        'text_color': text_color,
        'hover_color': (0, 128, 255),
        'is_hovered': False,
        'is_pressed': False
    }

def handle_button_event(button, event):
    """Handle events for a button"""
    if event.type == pygame.MOUSEMOTION:
        button['is_hovered'] = button['rect'].collidepoint(event.pos)
    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1 and button['rect'].collidepoint(event.pos):
            button['is_pressed'] = True
            return True
    elif event.type == pygame.MOUSEBUTTONUP:
        button['is_pressed'] = False
    return False

def draw_button(screen, button):
    """Draw a button"""
    color = button['hover_color'] if button['is_hovered'] else button['color']
    if button['is_pressed']:
        color = (0, 80, 160)
    
    pygame.draw.rect(screen, color, button['rect'])
    pygame.draw.rect(screen, (255, 255, 255), button['rect'], 2)
    
    text_surface = button['font'].render(button['text'], True, button['text_color'])
    text_rect = text_surface.get_rect(center=button['rect'].center)
    screen.blit(text_surface, text_rect)

def create_speed_slider(x, y, width, height, font, values, labels):
    """Create a speed slider dictionary"""
    return {
        'rect': pygame.Rect(x, y, width, height),
        'font': font,
        'values': values,
        'labels': labels,
        'current_index': 0,
        'dragging': False,
        'knob_radius': 10
    }

def handle_speed_slider_event(slider, event):
    """Handle events for a speed slider"""
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1 and slider['rect'].collidepoint(event.pos):
            slider['dragging'] = True
            return update_slider_from_mouse(slider, event.pos)
    elif event.type == pygame.MOUSEBUTTONUP:
        slider['dragging'] = False
    elif event.type == pygame.MOUSEMOTION and slider['dragging']:
        return update_slider_from_mouse(slider, event.pos)
    return False

def update_slider_from_mouse(slider, pos):
    """Update slider position from mouse"""
    relative_x = pos[0] - slider['rect'].x
    progress = max(0, min(1, relative_x / slider['rect'].width))
    new_index = round(progress * (len(slider['values']) - 1))
    
    if new_index != slider['current_index']:
        slider['current_index'] = new_index
        return True
    return False

def get_slider_current_value(slider):
    """Get current slider value"""
    return slider['values'][slider['current_index']]

def get_slider_current_label(slider):
    """Get current slider label"""
    return slider['labels'][slider['current_index']]

def draw_speed_slider(screen, slider):
    """Draw a speed slider"""
    # Draw slider track
    track_rect = pygame.Rect(slider['rect'].x, slider['rect'].centery - 2, slider['rect'].width, 4)
    pygame.draw.rect(screen, (100, 100, 100), track_rect)
    
    # Draw position markers
    for i in range(len(slider['values'])):
        marker_x = slider['rect'].x + (i / (len(slider['values']) - 1)) * slider['rect'].width
        pygame.draw.circle(screen, (150, 150, 150), (int(marker_x), slider['rect'].centery), 3)
    
    # Draw knob
    knob_x = slider['rect'].x + (slider['current_index'] / (len(slider['values']) - 1)) * slider['rect'].width
    pygame.draw.circle(screen, (255, 255, 255), (int(knob_x), slider['rect'].centery), slider['knob_radius'])
    pygame.draw.circle(screen, (0, 102, 204), (int(knob_x), slider['rect'].centery), slider['knob_radius'] - 2)
    
    # Draw label
    label_surface = slider['font'].render(f"Speed: {get_slider_current_label(slider)}", True, (255, 255, 255))
    label_rect = label_surface.get_rect(center=(slider['rect'].centerx, slider['rect'].y - 15))
    screen.blit(label_surface, label_rect)
    
    

# Debug flags - set to True only when needed
DEBUG_FILE_PARSING = False
DEBUG_BEAT_ANALYSIS = False  # Changed to False - use Debug button to toggle
DEBUG_GAME_LOOP = False
DEBUG_POSITIONS = False
DEBUG_TIMING = False
TEMP_DEBUG = False  # Temporary debug flag for parsing issue

# Original controls image coordinates (2040 x 3708 pixels) - from HTML version
ORIGINAL_CONTROLS_SIZE = {"width": 2040, "height": 3708}

# Button coordinates from original controls image (as polygons)
BUTTON_COORDS_ORIGINAL = {
    "playback_mode": [[200, 30], [1800, 30], [1800, 180], [200, 180]],
    "forward": [[63, 1953], [1866, 1851], [1888, 2048], [79, 2166]],
    "fast_rewind": [[162, 1242], [1011, 1207], [1038, 1411], [189, 1455]],
    "fast_forward": [[1216, 1216], [1987, 1194], [2010, 1393], [1251, 1413]],
    "pause": [[1170, 2632], [1944, 2563], [1966, 2766], [1197, 2844]],
    "stop_eject": [[154, 3454], [1934, 3229], [1956, 3434], [176, 3666]],
    "record": [[136, 2702], [976, 2619], [1002, 2844], [124, 2929]]
}

pygame.mixer.init()
try:
    click_sound = pygame.mixer.Sound("assets/click.wav")
except FileNotFoundError:
    click_sound = None
    print("Click sound file not found")

# Global variables for scaled button coordinates
scaled_button_coords = {}
playback_mode = "normal"  # normal, playback_idle, playback_active

def scale_button_coordinates(original_coords, original_image_size, scaled_image_size):
    """Scale button coordinates from original image to scaled image"""
    scale_x = scaled_image_size["width"] / original_image_size["width"]
    scale_y = scaled_image_size["height"] / original_image_size["height"]
    
    return [[int(coord[0] * scale_x), int(coord[1] * scale_y)] for coord in original_coords]

def offset_coordinates(coords, offset_x, offset_y):
    """Add offset to all coordinates"""
    return [[coord[0] + offset_x, coord[1] + offset_y] for coord in coords]

def point_in_polygon(point, polygon):
    """Check if point is inside polygon using ray casting algorithm"""
    x, y = point[0], point[1]
    inside = False
    
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside

def check_button_click(pos, button_coords):
    """Check which button (if any) was clicked"""
    for button_name, coords in button_coords.items():
        if point_in_polygon(pos, coords):
            return button_name
    return None

def calculate_controls_size():
    """Calculate controls image display size"""
    controls_height = screen_height // 3 + 72
    controls_width = int(controls_height * (ORIGINAL_CONTROLS_SIZE["width"] / ORIGINAL_CONTROLS_SIZE["height"]))
    return controls_width, controls_height

def scale_button_coords():
    """Scale all button coordinates based on current controls image size"""
    global scaled_button_coords
    scaled_button_coords = {}
    
    if controls_image:
        controls_width, controls_height = calculate_controls_size()
        controls_x = 20
        controls_y = screen_height - controls_height - 20
        
        scaled_image_size = {"width": controls_width, "height": controls_height}
        
        for button_name, coords in BUTTON_COORDS_ORIGINAL.items():
            # Scale to current image size
            scaled_coords = scale_button_coordinates(coords, ORIGINAL_CONTROLS_SIZE, scaled_image_size)
            # Offset to screen position
            final_coords = offset_coordinates(scaled_coords, controls_x, controls_y)
            scaled_button_coords[button_name] = final_coords

def handle_controls_click(mouse_pos):
    """Handle clicks on the controls image buttons"""
    global waiting_for_start, current_index, song_paused, bounce_start_time, bounce_count
    global playback_mode, pause_time, ball_y, song_line_number, DEBUG_BEAT_ANALYSIS
    
    clicked_button = check_button_click([mouse_pos[0], mouse_pos[1]], scaled_button_coords)
    
    if clicked_button:
        current_time = time.time()
        print(f"Controls button clicked: {clicked_button}")
        
        if clicked_button == "playback_mode":
            # Cycle through playback modes
            if playback_mode == "normal":
                playback_mode = "playback_idle"
                print("Switched to playback mode (idle)")
            elif playback_mode == "playback_idle":
                playback_mode = "playback_active"
                print("Started playback mode (active)")
            else:
                playback_mode = "normal"
                print("Returned to normal mode")
                
        elif clicked_button == "forward":
            # Main play/pause button
            if waiting_for_start:
                waiting_for_start = False
                bounce_start_time = current_time
                song_paused = False
                print("Started from controls")
            elif song_paused:
                # Resume - adjust bounce_start_time for pause duration
                pause_duration = current_time - pause_time
                bounce_start_time += pause_duration
                song_paused = False
                print("Resumed from controls")
            else:
                # Pause
                song_paused = True
                pause_time = current_time
                print("Paused from controls")
                                
        elif clicked_button == "fast_forward":
            # Jump to next line - check actual array bounds                  

            if current_index < len(lyrics) - 1:
                current_index += 1
                bounce_count = 0
                bounce_start_time = current_time
                ball_y = BALL_HIGH_POSITION
                song_line_number += 1
                print(f"Fast forward to line {current_index + 1}")
            else:
                print(f"Already at last line {len(lyrics) + 1})")                      
                
        elif clicked_button == "fast_rewind":
            # Jump to previous line
            if current_index > 0:
                current_index -= 1
                bounce_count = 0
                bounce_start_time = current_time
                ball_y = BALL_HIGH_POSITION
                song_line_number -= 1
                print(f"Rewind to line {current_index + 1}")
            else:
                print("Already at first line")              
                
        elif clicked_button == "pause":
            # Pause/unpause toggle
            if not waiting_for_start:
                if song_paused:
                    pause_duration = current_time - pause_time
                    bounce_start_time += pause_duration
                    song_paused = False
                    print("Unpaused from controls")
                else:
                    song_paused = True
                    pause_time = current_time
                    print("Paused from controls")
                    
        elif clicked_button == "stop_eject":
            # Restart song
            current_index = 0
            bounce_count = 0
            waiting_for_start = True
            ball_y = BALL_HIGH_POSITION
            song_line_number = 1
            bounce_start_time = None
            song_paused = False
            print("Restarted from controls")
            
        elif clicked_button == "record":
            # Toggle debug mode
            DEBUG_BEAT_ANALYSIS = not DEBUG_BEAT_ANALYSIS
            print(f"Debug mode: {DEBUG_BEAT_ANALYSIS}")
            
        return True
    
    return False

def draw_button_outlines():
    """Draw outlines on the controls image buttons (for visual feedback)"""
    if not scaled_button_coords:
        return
        
    for button_name, coords in scaled_button_coords.items():
        if len(coords) < 3:
            continue
            
        # Choose color based on button type and state
        if button_name == "playback_mode":
            if playback_mode == "normal":
                color = (0, 180, 0)
            elif playback_mode == "playback_idle":
                color = (200, 200, 0)
            else:
                color = (200, 0, 0)
        elif button_name == "forward":
            color = (0, 255, 0)
        elif button_name == "pause":
            color = (255, 255, 0)
        elif button_name == "stop_eject":
            color = (255, 0, 0)
        elif button_name in ["fast_rewind", "fast_forward"]:
            color = (0, 150, 255)
        elif button_name == "record":
            color = (255, 50, 50) if DEBUG_BEAT_ANALYSIS else (0, 255, 0)
        else:
            color = (255, 255, 255)
            
        # Draw polygon outline
        if len(coords) >= 3:
            pygame.draw.polygon(screen, color, coords, 3)

CHORDS = [
    # Major and Minor Chords
    "C", "D", "E", "F", "G", "A", "B",
    "Cm", "Dm", "Em", "Fm", "Gm", "Am", "Bm",
    # Seventh Chords
    "C7", "D7", "E7", "F7", "G7", "A7", "B7",
    "Cm7", "Dm7", "Em7", "Fm7", "Gm7", "Am7", "Bm7",
    "Cmaj7", "Dmaj7", "Emaj7", "Fmaj7", "Gmaj7", "Amaj7", "Bmaj7",
    # Flat and Sharp Chords
    "C♭", "D♭", "E♭", "F♭", "G♭", "A♭", "B♭",
    "C♯", "D♯", "E♯", "F♯", "G♯", "A♯", "B♯",
    "C♭m", "D♭m", "E♭m", "F♭m", "G♭m", "A♭m", "B♭m",
    "C♯m", "D♯m", "E♯m", "F♯m", "G♯m", "A♯m", "B♯m",
    # Suspended, Augmented, Diminished, Add chords
    "Csus4", "Dsus4", "Esus4", "Fsus4", "Gsus4", "Asus4", "Bsus4",
    "Csus2", "Dsus2", "Esus2", "Fsus2", "Gsus2", "Asus2", "Bsus2",
    "Cdim", "Ddim", "Edim", "Fdim", "Gdim", "Adim", "Bdim",
    "Caug", "Daug", "Eaug", "Faug", "Gaug", "Aaug", "Baug",
    "Cadd9", "Dadd9", "Eadd9", "Fadd9", "Gadd9", "Aadd9", "Badd9"
]

# Complete syllable dictionary for multiple songs
SYLLABLE_DICT = {
    # High Flight words (spoken syllables)
    "slipped": ["slipped"],
    "surly": ["sur", "ly"], 
    "bonds": ["bonds"],
    "danced": ["danced"],
    "skies": ["skies"],
    "laughter": ["laugh", "ter"],
    "silvered": ["sil", "verd"],  # pronounced "sil-vurd"
    "wings": ["wings"],
    "climbed": ["climbed"],
    "joined": ["joined"],
    "tumbling": ["tum", "bling"],
    "mirth": ["mirth"],
    "delirious": ["de", "lir", "i", "ous"],
    "burning": ["burn", "ing"],
    "footless": ["foot", "less"],
    "halls": ["halls"],
    
    # Rainbow Connection words  
    "rainbow": ["rain", "bow"],
    "rainbows": ["rain", "bows"],
    "visions": ["vi", "sions"],
    "illusions": ["il", "lu", "sions"],
    "believe": ["be", "lieve"],
    "believed": ["be", "lieved"],
    "amazing": ["a", "maz", "ing"],
    "connection": ["con", "nec", "tion"],
    "dreamers": ["dream", "ers"],
    
    # Additional Rainbow Connection words
    "answered": ["an", "swered"],
    "morning": ["morn", "ing"],
    "stargazing": ["star", "gaz", "ing"],
    "probably": ["prob", "ab", "ly"],
    "voices": ["voic", "es"],
    "calling": ["call", "ing"],
    "sailors": ["sail", "ors"],
    "ignore": ["ig", "nore"],
    "supposed": ["sup", "posed"],
    "something": ["some", "thing"],
    "other": ["oth", "er"],
    "under": ["un", "der"],
    "magic": ["mag", "ic"],
    "asleep": ["a", "sleep"],
    "lovers": ["lov", "ers"],
    "someday": ["some", "day"],
    "only": ["on", "ly"],
    
    # Don't Think Twice words
    "wonder": ["won", "der"],
    "baby": ["ba", "by"],
    "never": ["nev", "er"],
    "somehow": ["some", "how"],
    "rooster": ["roos", "ter"],
    "window": ["win", "dow"],
    "reason": ["rea", "son"],
    "turnin": ["turn", "in"],
    "turning": ["turn", "ing"],
    "callin": ["call", "in"],
    "calling": ["call", "ing"],
    "thinkin": ["think", "in"],
    "thinking": ["think", "ing"],
    "wondrin": ["wond", "rin"],
    "wondering": ["won", "der", "ing"],
    "walking": ["walk", "ing"],
    "woman": ["wom", "an"],
    "wanted": ["want", "ed"],
    "treated": ["treat", "ed"],
    "better": ["bet", "ter"],
    "precious": ["pre", "cious"],
    "harmonica": ["har", "mon", "i", "ca"],
    "honey": ["hon", "ey"],
    "goodbye": ["good", "bye"],
    "talkin": ["talk", "in"],
    "talking": ["talk", "ing"],
    "kinda": ["kind", "a"],
    "wasted": ["wast", "ed"],
    # Additional Dylan syllables
    "travelin": ["trav", "el", "in"],
    "anymore": ["an", "y", "more"], 
    "farewell": ["fare", "well"],
    "unkind": ["un", "kind"],
    "anyway": ["an", "y", "way"],
    "somethin": ["some", "thin"]
}



# Global variable to store chord/word data
beat_chord_word_data = {}

def extract_item_at_position(line, char_index):
    """Extract the word/chord that starts at or near the given character position."""
    if char_index >= len(line):
        return ""
    
    # Find the start of the word/chord
    start = char_index
    while start > 0 and line[start-1] != ' ':
        start -= 1
    
    # Find the end of the word/chord
    end = char_index
    while end < len(line) and line[end] != ' ':
        end += 1
    
    return line[start:end].strip()

def extract_syllable_at_position(line, char_index):
    """Extract the specific syllable that the beat position points to."""
    if char_index >= len(line):
        return ""
    
    # Find the word at this position
    word_start = char_index
    while word_start > 0 and line[word_start-1] != ' ':
        word_start -= 1
    
    word_end = char_index
    while word_end < len(line) and line[word_end] != ' ':
        word_end += 1
    
    word = line[word_start:word_end].strip().lower()
    
    # Clean punctuation before dictionary lookup
    clean_word = word.strip(string.punctuation).lower()
    
    # Check if this is the first word of the line
    is_first_word = word_start == 0 or line[:word_start].strip() == ""
    
    # Look up syllables for this word
    if clean_word in SYLLABLE_DICT:
        syllables = SYLLABLE_DICT[clean_word]
        position_in_word = char_index - word_start
        
        # Special handling for known words
        if clean_word == "rainbow":
            result = "rain" if position_in_word < 4 else "bow"
        elif clean_word == "rainbows":  
            result = "rain" if position_in_word < 4 else "bows"
        else:
            # Calculate actual syllable boundaries based on character counts
            syllable_boundaries = []
            char_count = 0
            for syllable in syllables:
                char_count += len(syllable)
                syllable_boundaries.append(char_count)
            
            # Find which syllable contains this position
            result = syllables[-1]  # Default to last syllable
            for i, boundary in enumerate(syllable_boundaries):
                if position_in_word < boundary:
                    result = syllables[i]
                    break
    else:
        # If word not in dictionary, return the clean word (no punctuation)
        result = clean_word
    
    # Capitalize first word of line unless escaped with backslash
    original_word = line[word_start:word_end].strip()
    if is_first_word:
        # Check for escape character
        if original_word.startswith('\\'):
            # Remove escape character and keep lowercase
            result = result.lower()
        else:
            # Always capitalize first word unless escaped
            result = result.capitalize()
    
    return result

def extract_chords_and_words(chord_line, lyric_line, beat_positions):
    """Extract chords and words based on character positions."""
    results = []
    
    for beat_num, char_index in beat_positions:
        chord = extract_item_at_position(chord_line, char_index)
        word = extract_item_at_position(lyric_line, char_index)
        results.append((beat_num, chord, word))
    
    return results

global song_line_number, song_section_line_number, song_lyric_line_number
global song_chord_line_number, song_beat_line_number, song_current_section
global lines_in_section, cleaned_line, current_index, sections, chords, lyrics, beats

sections, chords, lyrics, beats = [], [], [], []

def find_beat_positions(beat_line: str) -> List[Tuple[int, int]]:
    beats = []
    for match in re.finditer(r'\d+', beat_line):
        beat_num = int(match.group())
        if 1 <= beat_num <= 15:  # Extended range for different time signatures
            beats.append((beat_num, match.start()))
    return beats  

def clean_text(text):
    """Remove extra spaces or symbols"""
    return text.strip()

waiting = False

# Initialize pygame first
pygame.init()

# Screen setup
clock = pygame.time.Clock()
screen_width = 1920
screen_height = 1020
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption("Bouncing Ball Teleprompter (BBT)")

# Font setup (needed for prompt)
chord_font = pygame.font.SysFont("Courier", 40, bold=True)
lyric_font = pygame.font.SysFont("Courier", 40, bold=True)
section_font = pygame.font.SysFont("Courier", 40, bold=True)
title_font = pygame.font.SysFont("Courier", 40, bold=True)
progress_font = pygame.font.SysFont("Courier", 40, bold=True)

# Create UI buttons and controls
button_font = pygame.font.SysFont("Courier", 24, bold=True)
small_font = pygame.font.SysFont("Courier", 18)

# Button positions (right side of screen)
button_x = screen_width - 180
play_pause_button = create_button(button_x, 80, 160, 40, "Play/Pause", button_font)
restart_button = create_button(button_x, 130, 160, 40, "Restart", button_font)
debug_button = create_button(button_x, 180, 160, 40, "Toggle Debug", button_font)

# Speed slider
speed_values = [1.0, 1.25, 1.5, 1.75, 2.0]
speed_labels = ["1.0x", "1.25x", "1.5x", "1.75x", "2.0x"]
speed_slider = create_speed_slider(button_x, 250, 160, 20, small_font, speed_values, speed_labels)

# Base bounce duration for speed calculations
BASE_BOUNCE_DURATION = 0.625

def load_song_file():
    """Try auto-load first, then show Windows file browser if needed"""
    # Try auto-loading default files first
    default_files = [
        "williams-ascher-rainbow-connection.txt",
        "lyrick_beats.txt",
        "high-flight.txt"
    ]

    for filename in default_files:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                print(f"Auto-loaded: {filename}")
                return f.read(), filename
        except FileNotFoundError:
            continue

    # Auto-load failed, show Windows file browser
    print("Auto-load failed. Opening Windows file browser...")
    from tkinter import Tk, filedialog
    root = Tk()
    root.withdraw()  # Hide main window
    filename = filedialog.askopenfilename(
        title="Select lyrics file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()

    if filename:
        with open(filename, "r", encoding="utf-8") as f:
            import os
            basename = os.path.basename(filename)
            return f.read(), basename
    else:
        print("No file selected")
        exit()

# Load song data using HTML-style approach
song_file_data, loaded_filename = load_song_file()

BACKGROUND_FILE = r"assets\background.jpg"
CONTROLS_FILE = r"assets\controls.jpg"
MAG_TAPE_FILE = r"assets\magtape.jpg"
ICON_FILE = r"assets\icon.png"

# Process the loaded song data
song_data = [line.rstrip() for line in song_file_data.split('\n') if line.strip()]

# Extract title and time signature (first two lines)
title = song_data[0] if len(song_data) > 0 else "[No title]"
time_signature_str = song_data[1] if len(song_data) > 1 else "4/4"

# Parse the time signature to get beats per measure
beats_per_measure, note_value = parse_time_signature(time_signature_str)
print(f"Parsed time signature: {beats_per_measure}/{note_value}")

# --- Use time signature, not guesses ---
# Beat numbers: taken directly from the file (not calculated here).
first_beat_line = beats[0] if beats else ""
BEAT_NUMBERS = [int(n) for n in re.findall(r'\d+', first_beat_line)]
print("Beat numbers (from file):", BEAT_NUMBERS)

# Bounces per line: set by time signature only.
if beats_per_measure == 3:      # 3/4 time
    BOUNCES_PER_LINE = 4        # Rainbow
elif beats_per_measure == 4:    # 4/4 time
    BOUNCES_PER_LINE = 8        # Dylan
else:
    BOUNCES_PER_LINE = beats_per_measure  # fallback for other signatures
    
# Adjust base bounce duration per song
if beats_per_measure == 3:      # Rainbow (3/4)
    BASE_BOUNCE_DURATION = 1.625
elif beats_per_measure == 4:    # Dylan (4/4)
    BASE_BOUNCE_DURATION = 1.625  # for slowed down testing
#    BASE_BOUNCE_DURATION = 0.625 # for full speed

print(f"Time signature: {beats_per_measure}/{note_value}")
print(f"Beat numbers for highlighting: {BEAT_NUMBERS}")
print(f"Bounces per line: {BOUNCES_PER_LINE}")



# Dynamically calculate LINES_IN_SONG based on actual file content
LINES_IN_SONG = max(28, len([line for line in song_data[2:] if 'LL' in line and 'ZZZ' in line]) // 3)

print(f"Detected song length: {LINES_IN_SONG} lines")

# Load icon after file selection
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
    if DEBUG_FILE_PARSING:
        print(f"Background image not found: {BACKGROUND_FILE}")
    background_image = None

# Load controls image (bottom left)
try:
    controls_image = pygame.image.load(CONTROLS_FILE)
    controls_height = screen.get_height() // 3 + 72
    controls_width = int(controls_image.get_width() * controls_height / controls_image.get_height())
    controls_image = pygame.transform.scale(controls_image, (controls_width, controls_height))
    # Scale button coordinates after loading controls image
    scale_button_coords()
except FileNotFoundError:
    if DEBUG_FILE_PARSING:
        print(f"Controls image not found: {CONTROLS_FILE}")
    controls_image = None

# Load mag tape image (top, full width)
try:
    mag_tape_image = pygame.image.load(MAG_TAPE_FILE)
    tape_height = screen.get_height() // 8
    mag_tape_image = pygame.transform.scale(mag_tape_image, (screen.get_width(), tape_height))
except FileNotFoundError:
    if DEBUG_FILE_PARSING:
        print(f"Mag tape image not found: {MAG_TAPE_FILE}")
    mag_tape_image = None

# Ball position constant
BALL_HIGH_POSITION = 230

# Y position constants
POSITION_TITLE = 120
POSITION_TIME_SIGNATURE = 150
POSITION_SECTION = 180
POSITION_CHORDS = 210
POSITION_LYRIC_LINE = 240
current_index = 0

# Get remaining lines for categorization
remaining_lines = song_data[2:] if len(song_data) > 2 else []

def check_for_chord_line(line, CHORDS):
    """Check if 40% or more elements of a line are present in chord list."""
    if not line:
        return False
    words = line.split()
    thirty_percent_count = int(0.4 * len(words))
    match_count = 0
    for word in words:
        # Clean word of brackets and punctuation for chord matching
        clean_word = word.replace('[', '').replace(']', '').strip()
        if clean_word in CHORDS:
            match_count += 1
    return match_count >= thirty_percent_count

def get_rid_of_LL(cleaned_line):
    """Remove LL markers and ZZZ indicators from lines"""
    cleaned_line = cleaned_line.expandtabs(4)
    Line = bytearray(cleaned_line, encoding='utf-8')
    if 'LL' in Line.decode('utf-8'):
        match = re.search(r'(\d{2})$', Line.decode('utf-8'))
        if match:
            last_two_digits = match.group(1)
            if DEBUG_BEAT_ANALYSIS:
                print("lyric line number =", last_two_digits)
            Line = Line[:-5]
            Line = Line.rstrip()
            if b'ZZZ' in Line:
                Line = Line[:-3]
                string = Line.decode('utf-8')
                if DEBUG_BEAT_ANALYSIS:
                    print("ZZZ removed, Line =", string)
    return Line.decode('utf-8')

def categorize_line(line):
    """Categorize lines into sections, chords, lyrics, or beats"""
    cleaned_line = clean_text(line)

    # Section headers have brackets with section names
    if "[" in cleaned_line and "]" in cleaned_line:
        cleaned_line = cleaned_line.rstrip("0123456789")
        lines_in_section = cleaned_line.rsplit("]", 1)[-1]
        line = cleaned_line
        get_rid_of_LL(line)
        return "sections"
    else:
        # Remove brackets from potential chord lines for analysis
        line_for_analysis = cleaned_line.replace('[', '').replace(']', '')
    
        if check_for_chord_line(cleaned_line, CHORDS):
            processed_line = line[:-5].rstrip()
            ll_number = processed_line[-2:]
            cleaned_line = get_rid_of_LL(cleaned_line)
            return "chords"

        pattern = r"[\a-zA-Z\s]+"
        match = re.search(pattern, cleaned_line)
        if match:
            if "ZZZ" not in cleaned_line:
                get_rid_of_LL(cleaned_line)
                return "lyrics"
            else:
                if "ZZZ" in cleaned_line:
                    beat1 = '1'
                    processed_line = cleaned_line[:-5].rstrip()
                    ll_number = processed_line[-2:]
                    cleaned_line = get_rid_of_LL(cleaned_line)
                    if DEBUG_BEAT_ANALYSIS:
                        print("cleaned_line=", cleaned_line)
                    new_line = find_beat_positions(cleaned_line)
                    if DEBUG_BEAT_ANALYSIS:
                        print("new_line=", new_line)
                    return "beats"
    
# Categorize remaining lines into respective arrays
for i, line in enumerate(remaining_lines):
    line_type = categorize_line(line)
    if TEMP_DEBUG:
        print(f"Parsing line {i}: '{line}' -> categorized as: {line_type}")
    if line_type == "sections":
        sections.append(line)    
    elif line_type == "chords":
        chords.append(line)
    elif line_type == "lyrics":
        lyrics.append(line)
    elif line_type == "beats":
        beats.append(line)
        
        # Extract chord/word data for this beat line
        cleaned_beat_line = get_rid_of_LL(line)
        beat_positions = find_beat_positions(cleaned_beat_line)
        
        # Find corresponding chord and lyric lines
        beat_line_index = len(beats) - 1
        
        if beat_line_index < len(chords) and beat_line_index < len(lyrics):
            chord_line = get_rid_of_LL(chords[beat_line_index])
            lyric_line = get_rid_of_LL(lyrics[beat_line_index])

            # Extract the chord/word data
            chord_word_data = extract_chords_and_words(chord_line, lyric_line, beat_positions)
            beat_chord_word_data[beat_line_index] = chord_word_data
            
            if DEBUG_BEAT_ANALYSIS:
                print(f"chord_line after get_rid=", chord_line)
                print(f"lyric_line after get_rid=", lyric_line)
                print(f"beat_positions =", beat_positions)
                print(f"Line {beat_line_index} chord/word data: {chord_word_data}")

# Debug output
if DEBUG_BEAT_ANALYSIS: 
    print(f"Found {len(sections)} sections, {len(chords)} chords, {len(lyrics)} lyrics, {len(beats)} beats.")
    print(f"Sections: {sections[:5]}...")  # Show first 5 sections

current_index = 0

if DEBUG_BEAT_ANALYSIS: 
    print(f"Lyric: {lyrics[current_index % len(lyrics)]}")
    print(f"Chord: {chords[current_index % len(chords)]}")
    print(f"Beat: {beats[current_index % len(beats)]}")

# Initialize lists and dictionaries
indexes = []
current_indexes = []
beat_line_indexes = {}
beat_counter = 1

for current_index in range(min(LINES_IN_SONG, len(lyrics), len(chords), len(beats))):
    if current_index < len(lyrics):
        line = lyrics[current_index]
        line = get_rid_of_LL(line)
        lyrics[current_index] = line
    
    if current_index < len(chords):
        line = chords[current_index]
        line = get_rid_of_LL(line)
        chords[current_index] = line
    
    if current_index < len(beats):
        line = beats[current_index]
        line = get_rid_of_LL(line)
        beats[current_index] = line

# Pre-render title and time signature surfaces
title_surface = title_font.render(title, True, (0, 255, 0))
time_sig_surface = title_font.render(time_signature_str, True, (0, 255, 0))

# Timing calculations
BOUNCE_DURATION = BASE_BOUNCE_DURATION
FLASH_DURATION = BOUNCE_DURATION/4
print(f"FLASH_DURATION = {FLASH_DURATION}")
print(f"BOUNCES_PER_LINE = {BOUNCES_PER_LINE}")

index_at_new_section = 0
waiting = True
lines_in_section = 0

# Ball properties for realistic bouncing
ball_center_x = screen.get_width() // 2
ball_radius = 25
ball_top = BALL_HIGH_POSITION
ball_bottom = screen.get_height() - 100

# Calculate gravity needed for realistic bounce physics
fall_time = BOUNCE_DURATION / 2
bounce_height = ball_bottom - ball_top
gravity = (2 * bounce_height) / (fall_time ** 2)

def calculateGravity():
    """Recalculate gravity when bounce duration changes"""
    global gravity
    fall_time = BOUNCE_DURATION / 2
    bounce_height = ball_bottom - ball_top
    gravity = (2 * bounce_height) / (fall_time ** 2)

def calculate_pixel_position(text, font, start_x, char_index):
    """Calculate exact pixel X position where character index appears when text is rendered"""
    if char_index >= len(text):
        return start_x
    
    text_before = text[:char_index]
    text_surface = font.render(text_before, True, (255, 255, 255))
    return start_x + text_surface.get_width()

def render_word_at_position(word, font, x_pos, y_pos, color):
    """Render a single word at exact pixel coordinates"""
    word_surface = font.render(word, True, color)
    screen.blit(word_surface, (x_pos, y_pos))
    return word_surface.get_width()

def render_full_line_except_words(text, font, x_pos, y_pos, default_color, skip_positions):
    """Render full line but draw background rectangles over words at skip_positions"""
    full_surface = font.render(text, True, default_color)
    screen.blit(full_surface, (x_pos, y_pos))
    
    for char_index, word in skip_positions:
        word_pixel_x = calculate_pixel_position(text, font, x_pos, char_index)
        word_surface = font.render(word, True, default_color)
        pygame.draw.rect(screen, (30, 30, 30), (word_pixel_x, y_pos, word_surface.get_width(), word_surface.get_height()))

def handle_play_pause_action(waiting_for_start, current_index, current_time, song_paused, pause_time, bounce_start_time):
    """Handle play/pause functionality (used by both buttons and keys)"""
    if waiting_for_start:
        if current_index > 0:
            current_index = 0
        waiting_for_start = False
        bounce_start_time = current_time
    elif song_paused:
        pause_duration = current_time - pause_time
        bounce_start_time += pause_duration
        song_paused = False
    else:
        song_paused = True
        pause_time = current_time
    
    return waiting_for_start, current_index, song_paused, pause_time, bounce_start_time

# ✅ Extract beat numbers from the file before the main loop starts
global BEAT_NUMS
if beats:
    first_beat_line = beats[0]
    BEAT_NUMS = [int(n) for n in re.findall(r'\d+', first_beat_line)]
    print("Beat numbers (from file):", BEAT_NUMS)
else:
    BEAT_NUMS = []
    print("⚠️ No beat numbers found in file!")

# Main game loop
running = True

while running:
    # Reset all variables for new song
    current_index = 0
    bounce_count = 0
    flash_bounce1 = 1
    ball_y = BALL_HIGH_POSITION
    velocity_y = 0
    bounce_start_time = None
    song_paused = False
    pause_time = 0
    waiting_for_start = True
    dragging = False
    song_line_number = 1
    reuse_previous_section = False
    rising = False
    falling = True
    
    # Song playing loop
    while True:
        current_time = time.time()

        # Draw background
        if waiting_for_start and current_index > 0:
            if background_image:
                screen.blit(background_image, (0, 0))
            else:
                screen.fill((30, 30, 30))
        elif background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((30, 30, 30))

        # Draw mag tape at top and store circle position for click detection
        circle_center_x = None
        circle_center_y = None
        if mag_tape_image:
            screen.blit(mag_tape_image, (0, 0))

            # Draw position indicator
            if not waiting_for_start:
                indicator_width = 8
                position_x = int((current_index / len(lyrics)) * screen.get_width())
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

        # Draw controls at bottom left
        if controls_image:
            controls_y = screen.get_height() - controls_image.get_height() - 20
            controls_x = 20
            screen.blit(controls_image, (controls_x, controls_y))

            # Calculate and cache scaled button coordinates
            if not scaled_button_coords:
                scale_button_coords()
            
            # Draw button outlines for visual feedback
            draw_button_outlines()

            if not waiting_for_start:
                display_line_number = song_line_number
                progress_text = f"{display_line_number:03d}"
                progress_surface = progress_font.render(progress_text, True, (0, 255, 0))
                progress_x = controls_x + 50
                progress_y = controls_y + 20
                screen.blit(progress_surface, (progress_x, progress_y))

        # Always display title and time signature
        screen.blit(title_surface, (50, POSITION_TITLE))
        filename_surface = small_font.render(f"File: {loaded_filename}", True, (150, 150, 150))
        screen.blit(filename_surface, (50, POSITION_TITLE + 35))
        screen.blit(time_sig_surface, (50, POSITION_TIME_SIGNATURE))

        # Show start/restart message when waiting
        if waiting_for_start:
            if current_index == 0:
                restart_text = title_font.render("Spacebar or Play button to start", True, (255, 255, 255))
            else:
                restart_text = title_font.render("Spacebar or Play button to restart", True, (255, 255, 255))

            text_x = screen.get_width() - restart_text.get_width() - 50
            text_y = screen.get_height() - 200
            screen.blit(restart_text, (text_x, text_y))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_SPACE:
                    waiting_for_start, current_index, song_paused, pause_time, bounce_start_time = handle_play_pause_action(
                        waiting_for_start, current_index, current_time, song_paused, pause_time, bounce_start_time)
                elif event.key == pygame.K_r:
                    current_index = 0
                    bounce_count = 0
                    waiting_for_start = True
                    ball_y = BALL_HIGH_POSITION
                    song_line_number = 1
                    bounce_start_time = None
                    song_paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    clicked_something = False
                    
                    # Check for clicks on the controls image buttons FIRST
                    if scaled_button_coords:
                        if handle_controls_click(event.pos):
                            clicked_something = True
                    
                    # Check for clicks on the mag tape progress indicator
                    if circle_center_x is not None and circle_center_y is not None and not clicked_something:
                        circle_distance = ((mouse_x - circle_center_x) ** 2 + (mouse_y - circle_center_y) ** 2) ** 0.5
                        if circle_distance <= 25:
                            dragging = True
                            song_paused = True
                            waiting_for_start = False
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    dragging = False
                    song_paused = False
                    bounce_count = 0
                    bounce_start_time = current_time
                    ball_y = BALL_HIGH_POSITION
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    new_index = int((mouse_x / screen.get_width()) * LINES_IN_SONG)
                    new_index = max(0, min(new_index, LINES_IN_SONG - 1))
                    if new_index != current_index:
                        current_index = new_index

            # Handle button events
            if handle_button_event(play_pause_button, event):
                waiting_for_start, current_index, song_paused, pause_time, bounce_start_time = handle_play_pause_action(
                    waiting_for_start, current_index, current_time, song_paused, pause_time, bounce_start_time)

            if handle_button_event(restart_button, event):
                current_index = 0
                bounce_count = 0
                waiting_for_start = True
                ball_y = BALL_HIGH_POSITION
                song_line_number = 1
                bounce_start_time = None
                song_paused = False

            if handle_button_event(debug_button, event):
                DEBUG_BEAT_ANALYSIS = not DEBUG_BEAT_ANALYSIS
                print(f"Debug mode: {DEBUG_BEAT_ANALYSIS}")

            if handle_speed_slider_event(speed_slider, event):
                speed_multiplier = get_slider_current_value(speed_slider)
                BOUNCE_DURATION = BASE_BOUNCE_DURATION / speed_multiplier
                calculateGravity()
                print(f"Speed: {get_slider_current_label(speed_slider)} (Duration: {BOUNCE_DURATION:.3f}s)")

        if not running:
            break

        # Start the song if ready
        if waiting_for_start and current_index == 0 and not dragging:
            ball_y = BALL_HIGH_POSITION
            pygame.draw.circle(screen, (0, 255, 0), (ball_center_x, int(ball_y)), ball_radius)
            
            # Draw UI buttons and controls
            draw_button(screen, play_pause_button)
            draw_button(screen, restart_button)
            draw_button(screen, debug_button)
            draw_speed_slider(screen, speed_slider)

            BEAT_NUMBERS = BEAT_NUMS

            # Draw controls help text
            help_text = [
                f"Time Signature: {beats_per_measure}/{note_value}",
                f"Bounces per line: {BOUNCES_PER_LINE}",
                f"Beat numbers: {BEAT_NUMBERS}",
                "",
                "KEYBOARD:",
                "Space: Play/Pause",
                "R: Restart", 
                "Q: Quit",
                "Esc: Quit",
                "",
                "CONTROLS IMAGE:",
                "Forward (green): Play/Pause",
                "Fast Forward/Rewind: Line skip",
                "Pause (yellow): Pause toggle",
                "Stop (red): Restart",
                "Record (changes color): Debug",
                "Playback Mode (top): Mode cycle"
            ]
            for i, text in enumerate(help_text):
                color = (150, 150, 150) if text in ["KEYBOARD:", "CONTROLS IMAGE:", ""] else (200, 200, 200)
                help_surface = small_font.render(text, True, color)
                screen.blit(help_surface, (button_x, 300 + i * 18))
            
            pygame.display.flip()
            clock.tick(60)
            continue

        # Check if current bounce should be highlighted based on beat data
        should_highlight_ball = False
        should_highlight_chord = False
        should_highlight_word = False
        
        if current_index in beat_chord_word_data and rising:
            current_beat_data = beat_chord_word_data[current_index]
            current_beat_number = BEAT_NUMBERS[bounce_count % len(BEAT_NUMBERS)]
                        
            if DEBUG_BEAT_ANALYSIS: 
                print(f"Line {current_index}, Bounce {bounce_count}, Beat {current_beat_number}")
                print(f"Beat data: {current_beat_data}")
    
            for beat_num, chord, word in current_beat_data:
                if DEBUG_BEAT_ANALYSIS: 
                    print(f"  Comparing beat_num {beat_num} with current_beat_number {current_beat_number}")
                    breakpoint()
                if beat_num == current_beat_number:
                    if word != "":
                        should_highlight_ball = True
                        should_highlight_word = True
                    
                    should_highlight_chord = True
                    
                    if DEBUG_BEAT_ANALYSIS: 
                        print(f"Beat {beat_num}: chord='{chord}' word='{word}' | Ball={should_highlight_ball} Chord={should_highlight_chord} Word={should_highlight_word}")
                    break

        # Display text once song has started or when waiting after song ended
        if (not waiting_for_start or (waiting_for_start and current_index > 0)) and not dragging:
            # Display current section
            if sections and current_index < len(sections):
                song_current_section = sections[current_index % len(sections)]
                section_surface = section_font.render(song_current_section, True, (0, 0, 255))
                screen.blit(section_surface, (50, POSITION_SECTION))      
                                
            if chords and lyrics and current_index < len(chords) and current_index < len(lyrics):
                chord_text = chords[current_index].replace('[', '').replace(']', '')
                lyric_text = lyrics[current_index]
                
                # Check if highlighting is active
                highlighting_active = False
                skip_chord_positions = []
                skip_lyric_positions = []
                
                if current_index in beat_chord_word_data and rising:
                    current_beat_data = beat_chord_word_data[current_index]
                    current_beat_number = BEAT_NUMBERS[bounce_count % len(BEAT_NUMBERS)]
                    
                    for beat_num, chord, word in current_beat_data:
                        if beat_num == current_beat_number:
                            highlighting_active = True
                            if current_index < len(beats):
                                beat_positions = find_beat_positions(get_rid_of_LL(beats[current_index]))
                                
                                for b_num, char_index in beat_positions:
                                    if b_num == beat_num:
                                        if chord:
                                            skip_chord_positions.append((char_index, chord))
                                        if word:
                                            syllable = extract_syllable_at_position(lyric_text, char_index)
                                            skip_lyric_positions.append((char_index, syllable))
                                        break
                            break
                
                if highlighting_active:
                    # Render lines but skip highlighted words
                    render_full_line_except_words(chord_text, chord_font, 50, POSITION_CHORDS, (255, 165, 0), skip_chord_positions)
                    render_full_line_except_words(lyric_text, lyric_font, 50, POSITION_LYRIC_LINE, (255, 255, 255), skip_lyric_positions)
                    
                    # Render highlighted words at exact positions
                    dt = current_time - bounce_start_time
                    beat_progress = (dt % BOUNCE_DURATION) / BOUNCE_DURATION
                    beat_factor = beat_progress if rising else (1.0 - beat_progress)
                    
                    for char_index, word in skip_lyric_positions:
                        pixel_x = calculate_pixel_position(lyric_text, lyric_font, 50, char_index)
                        highlight_color = interpolate_color((255, 255, 255), (0, 255, 255), beat_factor)
                        render_word_at_position(word, lyric_font, pixel_x, POSITION_LYRIC_LINE, highlight_color)
                        
                    for char_index, chord in skip_chord_positions:
                        pixel_x = calculate_pixel_position(chord_text, chord_font, 50, char_index)
                        highlight_color = interpolate_color((255, 165, 0), (255, 255, 0), beat_factor)
                        render_word_at_position(chord, chord_font, pixel_x, POSITION_CHORDS, highlight_color)
                else:
                    # Normal rendering
                    chord_surface = chord_font.render(chord_text, True, (255, 165, 0))
                    screen.blit(chord_surface, (50, POSITION_CHORDS))
                    lyric_surface = lyric_font.render(lyric_text, True, (255, 255, 255))
                    screen.blit(lyric_surface, (50, POSITION_LYRIC_LINE))

        ball_draw_x = ball_center_x + (144 if dragging else 0)
                  
        # Draw ball with dynamic coloring
        if should_highlight_ball and rising:
            pygame.draw.circle(screen, (0, 255, 0), (ball_draw_x, int(ball_y)), ball_radius)
        else:
            pygame.draw.circle(screen, (238, 118, 33, 255), (ball_draw_x, int(ball_y)), ball_radius)

        # Draw UI buttons and controls
        draw_button(screen, play_pause_button)
        draw_button(screen, restart_button)
        draw_button(screen, debug_button)
        draw_speed_slider(screen, speed_slider)

        # Draw time signature info in the help text
        help_text = [
            f"Time Signature: {beats_per_measure}/{note_value}",
            f"Bounces per line: {BOUNCES_PER_LINE}",
            f"Beat numbers: {BEAT_NUMBERS}",
            "",
            "KEYBOARD:",
            "Space: Play/Pause",
            "R: Restart", 
            "Q: Quit",
            "Esc: Quit",
            "",
            "CONTROLS IMAGE:",
            "Forward (green): Play/Pause",
            "Fast Forward/Rewind: Line skip",
            "Pause (yellow): Pause toggle",
            "Stop (red): Restart",
            "Record (changes color): Debug",
            "Playback Mode (top): Mode cycle"
        ]
        for i, text in enumerate(help_text):
            color = (150, 150, 150) if text in ["KEYBOARD:", "CONTROLS IMAGE:", ""] else (200, 200, 200)
            help_surface = small_font.render(text, True, color)
            screen.blit(help_surface, (button_x, 300 + i * 18))

        # If paused or dragging, skip timing logic
        if song_paused or dragging:
            pygame.display.flip()
            clock.tick(60)
            continue

        # If waiting for start, keep ball at top
        if waiting_for_start:
            ball_y = BALL_HIGH_POSITION
            pygame.display.flip()
            clock.tick(60)
            continue

        dt = current_time - bounce_start_time

        # Realistic ball motion with gravity
        if dt <= BOUNCE_DURATION:
            fall_time = BOUNCE_DURATION / 2

            if dt <= fall_time:
                falling = True
                rising = False
                ball_y = ball_top + 0.5 * gravity * (dt ** 2)
                if ball_y >= ball_bottom:
                    ball_y = ball_bottom
            else:
                rise_time = dt - fall_time
                falling = False
                rising = True
                remaining_rise_time = fall_time - rise_time
                ball_y = ball_top + 0.5 * gravity * (remaining_rise_time ** 2)
                if ball_y < ball_top:
                    ball_y = ball_top
        else:
            # Complete bounce cycle - start new bounce
            bounce_start_time = current_time
            ball_y = ball_top
            velocity_y = 0
            bounce_count += 1
            
            # Advance text every BOUNCES_PER_LINE bounces
            if bounce_count >= BOUNCES_PER_LINE:
                
                
                
                
                bounce_count = 0
                if chords and lyrics:
                    if current_index < LINES_IN_SONG - 1:
                        current_index += 1
                        song_line_number += 1
                    else:   
                        waiting_for_start = True

        pygame.display.flip()
        clock.tick(60)

pygame.quit()
