# Automatic Lyrics Generator

Generate and display lyrics from audio files in real-time with cool ASCII art visualization!

## Features

- Convert audio files to text with timestamps
- Play audio with synchronized lyrics display
- Support for various audio formats
- Save lyrics to JSON format
- Cool ASCII art lyrics display
- Works even without all dependencies installed!

## Quick Start

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/JangkrikMc/liriklagu_otomatis.git
   cd liriklagu_otomatis
   ```

2. Run the installation script:
   ```bash
   ./install.sh
   ```

3. If the installation script doesn't work, you can run the application directly:
   ```bash
   # From the repository root directory
   ./bin/liriklagu
   
   # Or using Python directly
   python3 src/main.py
   ```

### Usage

1. Add audio files to the `audio` directory
2. Run the application:
   ```bash
   liriklagu
   ```
   
3. Select an audio file from the menu
4. Choose to convert the audio to lyrics or play with lyrics

## Command Line Options

```
usage: main.py [-h] [-f FILE] [-t] [-p] [-l] [-d DIRECTORY] [--no-audio]

Automatic Lyrics Generator

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Audio file to process
  -t, --transcribe      Transcribe the audio file
  -p, --play            Play audio with lyrics
  -l, --list            List available audio files
  -d, --directory, --directory DIRECTORY
                        Base directory for the application
  --no-audio            Run in lyrics-only mode without audio playback
```

## Troubleshooting

### The application says "Whisper is not installed"

The application will still work without Whisper, but with limited functionality. It will use a demo mode for lyrics generation.

### Audio playback doesn't work

The application will run in lyrics-only mode if audio playback libraries are not available. You can still see the lyrics display.

### The `liriklagu` command is not found

You can run the application directly using:
```bash
./bin/liriklagu
```
or
```bash
python3 src/main.py
```

## Dependencies

The application will try to work with whatever dependencies are available, but for full functionality, it needs:

- Python 3.6+
- FFmpeg
- Rich (for UI)
- Whisper (for transcription)
- Playsound (for audio playback)
- PyDub (for audio processing)

## License

This project is licensed under the MIT License - see the LICENSE file for details.