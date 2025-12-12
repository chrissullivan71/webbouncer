# Bouncing Ball Teleprompter (BBT)

A web-based bouncing ball teleprompter application for musical performances and karaoke-style displays.

## About

This project provides an interactive teleprompter that displays lyrics with synchronized chord progressions and a bouncing ball animation that follows the beat of the music. It's designed for performers, musicians, and anyone who wants to display song lyrics in a visually engaging way.

## Features

- **Bouncing Ball Animation**: A visual ball that bounces in sync with the music beat
- **Chord Display**: Shows chord progressions above lyrics
- **Multiple Song Support**: Load different songs with custom timing and metadata
- **Performance Controls**: Play, pause, and navigation controls
- **Customizable Timing**: Configurable beat patterns and bounce duration
- **Visual Assets**: Support for background images, icons, and themed elements

## Project Structure

- **HTML Performance Files**: Main application files (e.g., `performv14_renamed.html`)
- **Song Files**: Text files containing lyrics, chords, and structure (e.g., `the-visitor.txt`)
- **Metadata Files**: JSON files with song metadata and configuration (e.g., `the-visitor.json`)
- **Python Scripts**: Tools for song processing and format conversion
- **Assets**: Images, audio files, and visual elements

## Song Format

Songs follow a structured format with:
- Section headers (e.g., `[Verse 1]`, `[Chorus]`)
- Chord progressions
- Asterisks marking beat positions
- Beat numbers and timing codes

Example:
```
[Verse 1]
    G          D7       G       G7
    *          *        *       *
    Some lyrics here
    1          3        5       7
```

## Getting Started

1. Open `performv14_renamed.html` or `index.html` in a web browser
2. Select a song from the song selector dropdown
3. Use the control buttons to play, pause, or navigate through the performance

## Documentation

- See `TODOs.txt` for planned improvements and features
- See `docs/session-log-05-12-25.md` for development notes and session logs

## Version Notes

The project supports both V1 and V2 song formats with different rules for timing and enforcement.

## Contributing

This is a personal project by Chris Sullivan. If you have suggestions or find bugs related to the teleprompter functionality, please file an issue with:
- A clear description of the problem or suggestion
- Steps to reproduce (for bugs)
- Expected vs. actual behavior
- Browser and operating system information

## License

Copyright (c) 2025 Chris Sullivan. All rights reserved.

---

**Note**: For GitHub account-related questions (password resets, account cancellation, billing, etc.), please visit [GitHub Support](https://support.github.com/) or [GitHub Settings](https://github.com/settings/). This repository is for a teleprompter application and cannot assist with GitHub account issues.
