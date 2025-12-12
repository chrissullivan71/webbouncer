# Bouncing Ball Teleprompter (BBT)

A web-based teleprompter application that displays lyrics and text with a synchronized bouncing ball animation. Perfect for musicians, performers, and public speakers.

## Overview

Bouncing Ball Teleprompter is a client-side web application that helps performers follow along with lyrics, poems, or scripts using visual cues. The application features:

- **Bouncing ball animation** that highlights text in sync with the performance
- **Song/text file loading** with support for timing and beat information
- **Audio playback** for musical performances
- **Interactive controls** for play, pause, tempo adjustment, and more
- **No installation required** - runs entirely in your web browser

## Getting Started

1. Open `performv14_renamed.html` (or any of the HTML files) in a web browser
2. Select a song/text file using the dropdown selector
3. Press the Play button or click the canvas to start
4. Use the control buttons to adjust tempo, pause, or restart

## Features

- Real-time text highlighting synchronized with audio
- Adjustable tempo and playback controls
- Support for multiple song formats (V1 and V2)
- Drag-and-drop canvas positioning
- Debug mode for development

## File Structure

- `performv14_renamed.html` - Main application file
- `*.txt` - Song/lyric files with timing information
- `*.json` - Structured song data (V2 format)
- `*.mp3` - Audio files for musical performances
- `docs/` - Session logs and documentation

## FAQ

### How do I cancel my account?

**This application does not require an account or subscription.** Bouncing Ball Teleprompter is a free, open-source web application that runs entirely in your browser. There are:

- No accounts to create or cancel
- No subscriptions or payments required
- No data stored on any server
- No sign-up process

Simply close your browser tab when you're done using the application. All data remains on your local device.

### Do I need to install anything?

No installation is required. Simply open any of the HTML files in a modern web browser (Chrome, Firefox, Safari, or Edge recommended).

### Where is my data stored?

All data is stored locally on your device. The application does not send any information to external servers. Song files, audio files, and any customizations remain on your computer.

### How do I add my own songs?

Create a text file following the song format used in the existing `.txt` files in the repository. The format includes sections, chords, lyrics, and beat timing information.

### Is this free to use?

Yes, this is an open-source project. You can use, modify, and distribute it freely according to the project's license.

## Technical Details

This is a client-side JavaScript application with no backend requirements. It uses:
- HTML5 Canvas for rendering
- Web Audio API for audio playback
- Vanilla JavaScript (no framework dependencies)

## Contributing

Contributions are welcome! Please check the `TODOs.txt` file for current development priorities.

## Copyright

Copyright (c) 2025 Chris Sullivan. All rights reserved.

## Support

If you have questions or issues, please open an issue on the GitHub repository.
