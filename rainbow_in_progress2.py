import pygame
import time
import re
import pprint
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

# Debug flags - set to True only when needed
DEBUG_FILE_PARSING = False
DEBUG_BEAT_ANALYSIS = True
DEBUG_GAME_LOOP = False
DEBUG_POSITIONS = False
DEBUG_TIMING = False

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

# Syllable dictionary for High Flight and Rainbow Connection
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
    "amazing": ["a", "maz", "ing"],
    "connection": ["con", "nec", "tion"],
    "dreamers": ["dream", "ers"],
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
    
    # Look up syllables for this word
    if word in SYLLABLE_DICT:
        syllables = SYLLABLE_DICT[word]
        
        # Calculate which syllable the beat position points to
        position_in_word = char_index - word_start
        chars_per_syllable = len(word) / len(syllables)
        syllable_index = int(position_in_word / chars_per_syllable)
        syllable_index = min(syllable_index, len(syllables) - 1)
        
        return syllables[syllable_index]
    
    # If word not in dictionary, return the whole word
    return word

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
        if 1 <= beat_num <= 10:
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

def load_song_file():
    """Try auto-load first, then show file browser if needed (HTML-style approach)"""
    
    # Try auto-loading default files first (like HTML version)
    default_files = [
        "williams-ascher-rainbow-connection.txt",
        "lyrick_beats.txt", 
        "high-flight.txt"
    ]
    
    for filename in default_files:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                print(f"Auto-loaded: {filename}")
                return f.read()
        except FileNotFoundError:
            continue
    
    # Auto-load failed, show file browser (like HTML fallback)
    print("Auto-load failed. Opening file browser...")
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    filename = filedialog.askopenfilename(
        title="Select lyrics file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()
    
    if filename:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print("No file selected")
        exit()

# Load song data using HTML-style approach
song_file_data = load_song_file()

BACKGROUND_FILE = r"assets\background.jpg"
CONTROLS_FILE = r"assets\controls.jpg"
MAG_TAPE_FILE = r"assets\magtape.jpg"
ICON_FILE = r"assets\icon.png"
LINES_IN_SONG = 43

# Process the loaded song data
song_data = [line.rstrip() for line in song_file_data.split('\n') if line.strip()]

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

# Extract title and time signature (first two lines)
title = song_data[0] if len(song_data) > 0 else "[No title]"
time_signature = song_data[1] if len(song_data) > 1 else "[No time signature]"

# Get remaining lines for categorization
remaining_lines = song_data[2:] if len(song_data) > 2 else []

def check_for_chord_line(line, CHORDS):
    """Check if 40% or more elements of a line are present in chord list."""
    if not line:
        return False
    thirty_percent_count = int(0.4 * len(line.split()))
    match_count = 0
    for element in line:
        if element in CHORDS:
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
            
            print(f"chord_line after get_rid=", chord_line)
            print(f"lyric_line after get_rid=", lyric_line)
            print(f"beat_positions =", beat_positions)
            print(f"Line {beat_line_index} chord/word data: {chord_word_data}")

            # Debug: Check what the cleaned lines look like and where positions point
            if beat_line_index == 4:  # Line 5 (0-based)
                cleaned_chord = get_rid_of_LL(chords[4])
                cleaned_lyric = get_rid_of_LL(lyrics[4]) 
                cleaned_beat = get_rid_of_LL(beats[4])
         
                print(f"Cleaned chord: '{cleaned_chord}'")
                print(f"Cleaned lyric: '{cleaned_lyric}'")
                print(f"Cleaned beat:  '{cleaned_beat}'")         
                beat_positions = find_beat_positions(cleaned_beat)
                print(f"Beat positions: {beat_positions}")
                
                for beat_num, char_index in beat_positions:
                    chord_at_pos = extract_item_at_position(cleaned_chord, char_index)
                    word_at_pos = extract_item_at_position(cleaned_lyric, char_index)
                    print(f"Beat {beat_num} at position {char_index}: chord='{chord_at_pos}' word='{word_at_pos}'")

# Debug output
if DEBUG_BEAT_ANALYSIS: 
    print(f"Found {len(sections)} sections, {len(chords)} chords, {len(lyrics)} lyrics, {len(beats)} beats.")

# Add this debug code right after the beat parsing section to see what's happening with beat 10

print("=== DEBUGGING BEAT 10 ISSUE ===")

# Test the first few beat lines to see what's being found
for i in range(min(5, len(beats))):
    original_beat_line = beats[i]
    cleaned_beat_line = get_rid_of_LL(original_beat_line)
    beat_positions = find_beat_positions(cleaned_beat_line)
    
    print(f"\nBeat line {i}:")
    print(f"  Original: '{original_beat_line}'")
    print(f"  Cleaned:  '{cleaned_beat_line}'") 
    print(f"  Found beats: {beat_positions}")
    
    # Check specifically for beat 10
    has_beat_10 = any(beat_num == 10 for beat_num, pos in beat_positions)
    print(f"  Has beat 10: {has_beat_10}")
    
    # Show what's at position where beat 10 should be
    if has_beat_10:
        for beat_num, char_index in beat_positions:
            if beat_num == 10:
                print(f"  Beat 10 at position {char_index}: '{cleaned_beat_line[char_index:char_index+5]}'")

print("\n=== END DEBUG ===\n")

current_index = 0

if DEBUG_BEAT_ANALYSIS: 
    print(f"Lyric: {lyrics[current_index % len(lyrics)]}")
    print(f"Chord: {chords[current_index % len(chords)]}")
    print(f"Beat: {beats[current_index % len(beats)]}")
    print(f"Section: {sections[current_index % len(beats)]}")

# Initialize lists and dictionaries
indexes = []
current_indexes = []
beat_line_indexes = {}
beat_counter = 1

for current_index in range(27):
    line = lyrics[current_index]
    line = get_rid_of_LL(line)
    lyrics[current_index] = line
    
    line = chords[current_index]
    line = get_rid_of_LL(line)
    chords[current_index] = line
    
    line = beats[current_index]
    line = get_rid_of_LL(line)
    beats[current_index] = line
#    line = sections[current_index]
         
if DEBUG_BEAT_ANALYSIS: 
    print("Indexes of beats:", indexes)
    print(f"Lyrics: {lyrics[current_index]}")
    print(f"Chords: {chords[current_index]}")
    print(f"Beats: {beats[current_index]}")
#    print(f"Sections: {sections[current_index]}")

# Pre-render title and time signature surfaces
title_surface = title_font.render(title, True, (0, 255, 0))
time_sig_surface = title_font.render(time_signature, True, (0, 255, 0))

# Timing calculations based on 230 seconds song and 32 total lines
BOUNCE_DURATION = 1.625  # seconds per bounce
FLASH_DURATION = BOUNCE_DURATION/4
print("FLASH_DURATION =", FLASH_DURATION)
BOUNCES_PER_LINE = 4
BEAT_NUMBERS = [1, 4, 7, 10]
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
                position_x = int((current_index / 32) * screen.get_width())
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

            if not waiting_for_start:
                display_line_number = song_line_number
                progress_text = f"{display_line_number:03d}"
                progress_surface = progress_font.render(progress_text, True, (0, 255, 0))
                progress_x = controls_x + 50
                progress_y = controls_y + 20
                screen.blit(progress_surface, (progress_x, progress_y))

        # Always display title and time signature
        screen.blit(title_surface, (50, POSITION_TITLE))
        screen.blit(time_sig_surface, (50, POSITION_TIME_SIGNATURE))

        # Show start/restart message when waiting
        if waiting_for_start:
            if current_index == 0:
                restart_text = title_font.render("Spacebar to bounce", True, (255, 255, 255))
            else:
                restart_text = title_font.render("Press spacebar to restart", True, (255, 255, 255))

            text_x = screen.get_width() - restart_text.get_width() - 50
            text_y = screen.get_height() - 200
            screen.blit(restart_text, (text_x, text_y))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                    break
                elif event.key == pygame.K_SPACE:
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and circle_center_x is not None and circle_center_y is not None:
                    mouse_x, mouse_y = event.pos
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
                    new_index = int((mouse_x / screen.get_width()) * 32)
                    new_index = max(0, min(new_index, 31))
                    if new_index != current_index:
                        current_index = new_index

        if not running:
            break

        # Start the song if ready
        if waiting_for_start and current_index == 0 and not dragging:
            ball_y = BALL_HIGH_POSITION
            pygame.draw.circle(screen, (0, 255, 0), (ball_center_x, int(ball_y)), ball_radius)
            pygame.display.flip()
            clock.tick(60)
            continue

        # Check if current bounce should be highlighted based on beat data
        should_highlight_ball = False
        should_highlight_chord = False
        should_highlight_word = False
        
        if current_index in beat_chord_word_data:
            current_beat_data = beat_chord_word_data[current_index]
            current_beat_number = BEAT_NUMBERS[bounce_count]
                        
            if DEBUG_BEAT_ANALYSIS: 
                print(f"Line {current_index}, Bounce {bounce_count}, Beat {current_beat_number}")
                print(f"Beat data: {current_beat_data}")
    
            for beat_num, chord, word in current_beat_data:
                if DEBUG_BEAT_ANALYSIS: 
                    print(f"  Comparing beat_num {beat_num} with current_beat_number {current_beat_number}")
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
            if sections:
                song_current_section = (sections[current_index%len(sections)])
                section_surface = section_font.render(sections[current_index%len(sections)], True, (0, 0, 255))
                screen.blit(section_surface, (50, POSITION_SECTION))      
                                
            if chords and lyrics:
                chord_text = chords[current_index % len(chords)].replace('[', '').replace(']', '')
                lyric_text = lyrics[current_index % len(lyrics)]
                
                # Check if highlighting is active
                highlighting_active = False
                skip_chord_positions = []
                skip_lyric_positions = []
                
                if current_index in beat_chord_word_data and rising:
                    current_beat_data = beat_chord_word_data[current_index]
                    current_beat_number = BEAT_NUMBERS[bounce_count]
                    
                    for beat_num, chord, word in current_beat_data:
                        if beat_num == current_beat_number:
                            highlighting_active = True
                            beat_positions = find_beat_positions(get_rid_of_LL(beats[current_index]))
                            
                            for b_num, char_index in beat_positions:
                                if b_num == beat_num:
                                    if chord:
                                        skip_chord_positions.append((char_index, chord))
                                    if word:
                                       # Get the specific syllable instead of whole word
                                       syllable = extract_syllable_at_position(lyric_text, char_index)
                                       skip_lyric_positions.append((char_index, syllable))
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

            if beats and DEBUG_BEAT_ANALYSIS: 
                print(beats[current_index%len(beats)])                
                  
        ball_draw_x = ball_center_x + (144 if dragging else 0)
                  
        # Draw ball with dynamic coloring
        if should_highlight_ball and rising:
            pygame.draw.circle(screen, (0, 255, 0), (ball_draw_x, int(ball_y)), ball_radius)
        else:
            pygame.draw.circle(screen, (238, 118, 33, 255), (ball_draw_x, int(ball_y)), ball_radius)

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
            
            # Advance text every 8 bounces
            if bounce_count >= BOUNCES_PER_LINE:
                bounce_count = 0
                if chords and lyrics:
                    if current_index < LINES_IN_SONG:
                        current_index += 1
                        song_line_number += 1
                    else:   
                        waiting_for_start = True

        pygame.display.flip()
        clock.tick(60)

pygame.quit()
