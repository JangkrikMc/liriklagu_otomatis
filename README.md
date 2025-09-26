# 🎵 Automatic Lyrics Generator

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A beautiful and user-friendly application that automatically generates and displays lyrics from audio files in real-time. This tool uses OpenAI's Whisper model to transcribe audio and display synchronized lyrics as the music plays.

![Demo Screenshot](https://via.placeholder.com/800x400?text=Automatic+Lyrics+Generator)

## ✨ Features

- **Rich Interactive Interface**: Beautiful terminal UI with menus, progress bars, and colorful text
- **Audio File Selection**: Choose from available audio files or provide custom paths
- **Automatic Transcription**: Convert speech/singing to text with precise timestamps
- **Real-time Lyrics Display**: See lyrics synchronized with the audio playback
- **Multiple Audio Format Support**: Works with MP3, WAV, and other common formats
- **No Coding Required**: Fully menu-driven interface, no technical knowledge needed

## 📋 Requirements

- Python 3.8 or higher
- ffmpeg (for audio processing)
- Internet connection (for initial model download)

## 🚀 Installation

### Automatic Installation

1. Clone this repository:
```bash
git clone https://github.com/JangkrikMc/liriklagu_otomatis.git
cd liriklagu_otomatis
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Activate the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Manual Installation

If the automatic installation doesn't work, you can install manually:

1. Install ffmpeg:
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - MacOS: `brew install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the application:
```bash
python src/main.py
```

3. Follow the on-screen menu to:
   - Select an audio file
   - Generate lyrics
   - Play audio with synchronized lyrics

## 📁 Project Structure

```
liriklagu_otomatis/
├── audio/              # Directory for audio files
├── output/             # Generated lyrics files (JSON)
├── src/                # Source code
│   ├── main.py         # Main application script
│   └── test.py         # Test script
├── temp/               # Temporary files
├── install.sh          # Installation script
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🎵 Adding Your Own Audio Files

To use your own audio files:

1. Place your audio files in the `audio/` directory
2. Run the application and select your file from the menu
3. Generate lyrics and enjoy!

Supported formats: MP3, WAV, OGG, FLAC, M4A

## 🔧 How It Works

1. **Audio Processing**: The application converts your audio to the format required by the Whisper model
2. **Transcription**: OpenAI's Whisper model transcribes the audio with word-level timestamps
3. **Synchronization**: The application plays the audio while displaying lyrics in real-time
4. **Storage**: Lyrics are saved in JSON format for future use

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenAI Whisper](https://github.com/openai/whisper) for the speech recognition model
- [Rich](https://github.com/Textualize/rich) for the beautiful terminal interface
- [ffmpeg](https://ffmpeg.org/) for audio processing capabilities