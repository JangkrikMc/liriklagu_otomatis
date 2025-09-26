#!/usr/bin/env python3
"""
Automatic Lyrics Generator
A tool to automatically generate and display lyrics from audio files in real-time.
"""

import os
import sys
import json
import time
import threading
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Flag to track if modules are available
WHISPER_AVAILABLE = False
FFMPEG_AVAILABLE = False
RICH_AVAILABLE = False
PLAYSOUND_AVAILABLE = False
PYDUB_AVAILABLE = False

# Try to import required packages with fallbacks
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    print("Whisper is not installed. Some features will be limited.")
    # Create a mock whisper module for basic functionality
    class MockWhisper:
        @staticmethod
        def load_model(name):
            return MockWhisperModel()
    
    class MockWhisperModel:
        def transcribe(self, audio_path, **kwargs):
            print(f"[Mock] Would transcribe {audio_path}")
            return {"segments": []}
    
    whisper = MockWhisper()

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    print("ffmpeg-python is not installed. Some features will be limited.")
    # Create a mock ffmpeg module for basic functionality
    class MockFFmpeg:
        @staticmethod
        def input(file):
            return MockFFmpegInput(file)
    
    class MockFFmpegInput:
        def __init__(self, file):
            self.file = file
        
        def output(self, output_path, **kwargs):
            return MockFFmpegOutput(self.file, output_path)
    
    class MockFFmpegOutput:
        def __init__(self, input_file, output_path):
            self.input_file = input_file
            self.output_path = output_path
        
        def run(self, **kwargs):
            print(f"[Mock] Would convert {self.input_file} to {self.output_path}")
            # Try to copy the file as a fallback
            try:
                import shutil
                shutil.copy(self.input_file, self.output_path)
                print(f"[Mock] Copied file instead of converting")
            except Exception as e:
                print(f"[Mock] Failed to copy file: {e}")
    
    ffmpeg = MockFFmpeg()

# Try to import rich or create simple fallbacks
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    from rich.box import Box
    RICH_AVAILABLE = True
except ImportError:
    print("Rich is not installed. Using simple text interface.")
    
    # Create simple fallbacks for rich components
    class SimpleConsole:
        def print(self, *args, **kwargs):
            # Strip rich formatting
            text = str(args[0])
            for tag in ['[bold]', '[/bold]', '[italic]', '[/italic]', '[green]', '[/green]', 
                       '[blue]', '[/blue]', '[red]', '[/red]', '[yellow]', '[/yellow]',
                       '[cyan]', '[/cyan]', '[magenta]', '[/magenta]', '[white]', '[/white]']:
                text = text.replace(tag, '')
            print(text)
        
        def status(self, text):
            class MockStatus:
                def __enter__(self):
                    print(text)
                    return self
                
                def __exit__(self, *args):
                    pass
                
                def update(self, new_text):
                    print(new_text)
            
            return MockStatus()
        
        def print_exception(self):
            import traceback
            traceback.print_exc()
    
    class SimplePanel:
        @staticmethod
        def fit(text, **kwargs):
            return text
    
    class SimplePrompt:
        @staticmethod
        def ask(text, choices=None):
            print(text)
            if choices:
                print(f"Options: {', '.join(choices)}")
            return input("> ")
    
    class SimpleConfirm:
        @staticmethod
        def ask(text):
            response = input(f"{text} (y/n): ")
            return response.lower() in ['y', 'yes']
    
    class SimpleTable:
        def __init__(self, title=None, **kwargs):
            self.title = title
            self.columns = []
            self.rows = []
            if title:
                print(f"\n--- {title} ---")
        
        def add_column(self, header, **kwargs):
            self.columns.append(header)
        
        def add_row(self, *args):
            self.rows.append(args)
            print(" | ".join([str(arg) for arg in args]))
    
    class SimpleText:
        def __init__(self):
            self.content = ""
            self.plain = ""
        
        def append(self, text, **kwargs):
            self.content += text
            self.plain += text
            print(text, end="")
    
    class SimpleLayout:
        def __init__(self):
            self.sections = {}
        
        def split(self, *args):
            for arg in args:
                self.sections[arg.name] = arg
        
        def __getitem__(self, key):
            return self.sections.get(key, SimpleLayoutSection())
    
    class SimpleLayoutSection:
        def update(self, content):
            if hasattr(content, 'title'):
                print(f"\n--- {content.title} ---")
            print(content)
    
    class SimpleLive:
        def __init__(self, content, **kwargs):
            self.content = content
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
    
    class SimpleAlign:
        @staticmethod
        def center(text):
            return text
    
    # Assign the simple classes to the expected names
    Console = SimpleConsole
    Panel = SimplePanel
    Prompt = SimplePrompt
    Confirm = SimpleConfirm
    Table = SimpleTable
    Text = SimpleText
    Layout = SimpleLayout
    Live = SimpleLive
    Align = SimpleAlign
    Box = type('SimpleBox', (), {})
    Progress = type('SimpleProgress', (), {})
    SpinnerColumn = type('SimpleSpinnerColumn', (), {})
    TextColumn = type('SimpleTextColumn', (), {})
    BarColumn = type('SimpleBarColumn', (), {})
    TimeElapsedColumn = type('SimpleTimeElapsedColumn', (), {})

# Try to import playsound or create a fallback
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    try:
        # Try to use our fallback module
        from fallback import playsound
        print("Using fallback playsound module with ffplay")
        PLAYSOUND_AVAILABLE = True
    except ImportError:
        print("Audio playback libraries are not installed. Running in lyrics-only mode.")
        # Define a dummy playsound function that does nothing
        def playsound(sound_file, block=True):
            print(f"[Audio playback disabled] Would play: {sound_file}")
            return True

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    print("Pydub is not installed. Some features will be limited.")
    # Create a mock AudioSegment
    class MockAudioSegment:
        pass
    
    class MockPydub:
        AudioSegment = MockAudioSegment
    
    pydub = MockPydub()

# Initialize console
console = Console()

# ASCII Art generator function
def generate_ascii_art(text, style="standard"):
    """Generate ASCII art text for display"""
    # Simple ASCII art styles
    styles = {
        "standard": {
            'A': [' ▄▄▄▄▄ ', '█     █', '███████', '█     █', '█     █'],
            'B': ['██████ ', '█     █', '██████ ', '█     █', '██████ '],
            'C': [' █████ ', '█     █', '█      ', '█     █', ' █████ '],
            'D': ['██████ ', '█     █', '█     █', '█     █', '██████ '],
            'E': ['███████', '█      ', '█████  ', '█      ', '███████'],
            'F': ['███████', '█      ', '█████  ', '█      ', '█      '],
            'G': [' █████ ', '█      ', '█   ███', '█     █', ' █████ '],
            'H': ['█     █', '█     █', '███████', '█     █', '█     █'],
            'I': ['███████', '   █   ', '   █   ', '   █   ', '███████'],
            'J': ['███████', '     █ ', '     █ ', '█    █ ', ' ████  '],
            'K': ['█    █ ', '█   █  ', '████   ', '█   █  ', '█    █ '],
            'L': ['█      ', '█      ', '█      ', '█      ', '███████'],
            'M': ['█     █', '██   ██', '█ █ █ █', '█  █  █', '█     █'],
            'N': ['█     █', '██    █', '█ █   █', '█  █  █', '█   ███'],
            'O': [' █████ ', '█     █', '█     █', '█     █', ' █████ '],
            'P': ['██████ ', '█     █', '██████ ', '█      ', '█      '],
            'Q': [' █████ ', '█     █', '█     █', '█   █ █', ' ████ █'],
            'R': ['██████ ', '█     █', '██████ ', '█   █  ', '█    █ '],
            'S': [' █████ ', '█      ', ' █████ ', '      █', '██████ '],
            'T': ['███████', '   █   ', '   █   ', '   █   ', '   █   '],
            'U': ['█     █', '█     █', '█     █', '█     █', ' █████ '],
            'V': ['█     █', '█     █', '█     █', ' █   █ ', '  ███  '],
            'W': ['█     █', '█     █', '█  █  █', '█ █ █ █', '██   ██'],
            'X': ['█     █', ' █   █ ', '  ███  ', ' █   █ ', '█     █'],
            'Y': ['█     █', ' █   █ ', '  ███  ', '   █   ', '   █   '],
            'Z': ['███████', '    █  ', '   █   ', '  █    ', '███████'],
            ' ': ['       ', '       ', '       ', '       ', '       '],
            '!': ['   █   ', '   █   ', '   █   ', '       ', '   █   '],
            '?': [' █████ ', '█     █', '    ██ ', '       ', '   █   '],
            '.': ['       ', '       ', '       ', '       ', '   █   '],
            ',': ['       ', '       ', '       ', '   █   ', '  █    '],
            '0': [' █████ ', '█     █', '█     █', '█     █', ' █████ '],
            '1': ['   █   ', '  ██   ', '   █   ', '   █   ', '███████'],
            '2': [' █████ ', '█     █', '    ██ ', '  ██   ', '███████'],
            '3': [' █████ ', '      █', '   ███ ', '      █', ' █████ '],
            '4': ['█    █ ', '█    █ ', '███████', '     █ ', '     █ '],
            '5': ['███████', '█      ', '██████ ', '      █', '██████ '],
            '6': [' █████ ', '█      ', '██████ ', '█     █', ' █████ '],
            '7': ['███████', '     █ ', '    █  ', '   █   ', '  █    '],
            '8': [' █████ ', '█     █', ' █████ ', '█     █', ' █████ '],
            '9': [' █████ ', '█     █', ' ██████', '      █', ' █████ '],
            '-': ['       ', '       ', '███████', '       ', '       '],
            '_': ['       ', '       ', '       ', '       ', '███████'],
            '+': ['       ', '   █   ', ' █████ ', '   █   ', '       '],
            '=': ['       ', ' █████ ', '       ', ' █████ ', '       '],
            '*': ['       ', ' █ █ █ ', '  ███  ', ' █ █ █ ', '       '],
            '/': ['      █', '     █ ', '    █  ', '   █   ', '  █    '],
            '\\': ['█      ', ' █     ', '  █    ', '   █   ', '    █  '],
            '(': ['    █  ', '   █   ', '   █   ', '   █   ', '    █  '],
            ')': ['  █    ', '   █   ', '   █   ', '   █   ', '  █    '],
            '[': ['  ████ ', '  █    ', '  █    ', '  █    ', '  ████ '],
            ']': [' ████  ', '    █  ', '    █  ', '    █  ', ' ████  '],
            '{': ['    ██ ', '   █   ', '  ██   ', '   █   ', '    ██ '],
            '}': [' ██    ', '   █   ', '   ██  ', '   █   ', ' ██    '],
            '|': ['   █   ', '   █   ', '   █   ', '   █   ', '   █   '],
            ':': ['       ', '   █   ', '       ', '   █   ', '       '],
            ';': ['       ', '   █   ', '       ', '   █   ', '  █    '],
            '"': [' █   █ ', ' █   █ ', '       ', '       ', '       '],
            "'": ['   █   ', '   █   ', '       ', '       ', '       '],
            '`': ['   █   ', '    █  ', '       ', '       ', '       '],
            '~': ['       ', '  █  █ ', ' █ █   ', '       ', '       '],
            '^': ['   █   ', '  █ █  ', '       ', '       ', '       '],
            '&': ['  ██   ', ' █  █  ', '  ██ █ ', ' █  █  ', '  ██ █ '],
            '@': [' ████  ', '█    █ ', '█ ████ ', '█      ', ' ████  '],
            '#': [' █   █ ', '███████', ' █   █ ', '███████', ' █   █ '],
            '$': ['   █   ', ' █████ ', '█      ', ' █████ ', '   █   '],
            '%': ['██   █ ', '██  █  ', '   █   ', '  █  ██', ' █   ██'],
        }
    }
    
    # Convert text to uppercase for ASCII art
    text = text.upper()
    
    # Get the selected style or default to standard
    style_dict = styles.get(style, styles["standard"])
    
    # Generate ASCII art lines
    lines = ["", "", "", "", ""]
    for char in text:
        char_art = style_dict.get(char, style_dict[" "])
        for i in range(5):
            lines[i] += char_art[i]
    
    return lines

class LyricGenerator:
    """Main class for the Automatic Lyrics Generator application."""
    
    def __init__(self, base_dir=None):
        """Initialize the application."""
        # Determine the base directory
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            # Try to find the base directory
            script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            if (script_dir / '..' / 'audio').exists():
                # Running from source
                self.base_dir = script_dir.parent
            else:
                # Running from installed package or command
                self.base_dir = Path.cwd()
        
        self.audio_path = None
        self.output_dir = self.base_dir / "output"
        self.audio_dir = self.base_dir / "audio"
        self.temp_dir = self.base_dir / "temp"
        self.model = None
        self.lyrics = []
        
        # Create necessary directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def display_welcome(self) -> None:
        """Display welcome message and application info."""
        # Generate ASCII art for the title
        title_art = generate_ascii_art("LYRICS GENERATOR")
        
        # Display the ASCII art title
        for line in title_art:
            console.print(f"[bold blue]{line}[/bold blue]")
        
        console.print(Panel.fit(
            "[bold blue]Automatic Lyrics Generator[/bold blue]\n"
            "[italic]Generate and display lyrics from audio files in real-time[/italic]",
            border_style="blue",
            padding=(1, 10)
        ))
        
        # Display module availability status
        console.print("\n[bold]Module Status:[/bold]")
        status_table = Table(show_header=False, box=None)
        status_table.add_column(style="yellow")
        status_table.add_column(style="green")
        status_table.add_row("Whisper:", "Available ✓" if WHISPER_AVAILABLE else "Not Available ✗")
        status_table.add_row("FFmpeg:", "Available ✓" if FFMPEG_AVAILABLE else "Not Available ✗")
        status_table.add_row("Rich UI:", "Available ✓" if RICH_AVAILABLE else "Not Available ✗")
        status_table.add_row("Audio Playback:", "Available ✓" if PLAYSOUND_AVAILABLE else "Not Available ✗")
        status_table.add_row("PyDub:", "Available ✓" if PYDUB_AVAILABLE else "Not Available ✗")
        console.print(status_table)
        
        console.print("\n[bold]Features:[/bold]")
        features = Table(show_header=False, box=None)
        features.add_column(style="green")
        features.add_row("• Convert audio files to text with timestamps")
        features.add_row("• Play audio with synchronized lyrics display")
        features.add_row("• Support for various audio formats")
        features.add_row("• Save lyrics to JSON format")
        features.add_row("• Cool ASCII art lyrics display")
        console.print(features)
        console.print()
    
    def show_main_menu(self) -> str:
        """Display the main menu and return the selected option."""
        # Generate ASCII art for the menu title
        menu_art = generate_ascii_art("MAIN MENU")
        
        # Display the ASCII art menu title
        for line in menu_art:
            console.print(f"[bold cyan]{line}[/bold cyan]")
        
        options = [
            "Convert audio to lyrics",
            "Play audio with lyrics",
            "Select audio file",
            "View available audio files",
            "Exit"
        ]
        
        for i, option in enumerate(options, 1):
            console.print(f"  {i}. {option}")
        
        choice = Prompt.ask("\n[bold]Choose an option[/bold]", choices=[str(i) for i in range(1, len(options) + 1)])
        return choice
    
    def list_audio_files(self) -> List[str]:
        """List all audio files in the audio directory."""
        audio_files = []
        for file in os.listdir(self.audio_dir):
            if file.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a')):
                audio_files.append(file)
        return audio_files
    
    def display_audio_files(self) -> None:
        """Display a table of available audio files."""
        audio_files = self.list_audio_files()
        
        # Generate ASCII art for the title
        files_art = generate_ascii_art("AUDIO FILES")
        
        # Display the ASCII art title
        for line in files_art:
            console.print(f"[bold green]{line}[/bold green]")
        
        if not audio_files:
            console.print("[yellow]No audio files found in the audio directory.[/yellow]")
            console.print(f"Please add audio files to the [bold]{self.audio_dir}[/bold] directory.")
            return
        
        table = Table(title="Available Audio Files")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Filename", style="green")
        table.add_column("Size", style="magenta")
        
        for i, file in enumerate(audio_files, 1):
            file_path = self.audio_dir / file
            size = os.path.getsize(file_path)
            size_str = f"{size / 1024 / 1024:.2f} MB" if size > 1024 * 1024 else f"{size / 1024:.2f} KB"
            table.add_row(str(i), file, size_str)
        
        console.print(table)
    
    def select_audio_file(self) -> Optional[str]:
        """Let the user select an audio file."""
        audio_files = self.list_audio_files()
        
        # Generate ASCII art for the title
        select_art = generate_ascii_art("SELECT FILE")
        
        # Display the ASCII art title
        for line in select_art:
            console.print(f"[bold magenta]{line}[/bold magenta]")
        
        if not audio_files:
            console.print("[yellow]No audio files found in the audio directory.[/yellow]")
            console.print(f"Please add audio files to the [bold]{self.audio_dir}[/bold] directory.")
            return None
        
        self.display_audio_files()
        
        choice = Prompt.ask(
            "\n[bold]Select a file by ID[/bold]", 
            choices=[str(i) for i in range(1, len(audio_files) + 1)]
        )
        
        selected_file = audio_files[int(choice) - 1]
        self.audio_path = str(self.audio_dir / selected_file)
        console.print(f"[green]Selected:[/green] {selected_file}")
        return self.audio_path
    
    def convert_audio_to_wav(self, audio_path: str) -> str:
        """Convert audio file to WAV format for processing."""
        output_path = str(self.temp_dir / "temp_audio.wav")
        
        with console.status("[bold green]Converting audio to WAV format..."):
            try:
                if FFMPEG_AVAILABLE:
                    # Use ffmpeg to convert to WAV with proper settings for Whisper
                    ffmpeg.input(audio_path).output(
                        output_path, 
                        acodec='pcm_s16le',
                        ac=1,  # mono
                        ar=16000  # 16kHz sample rate
                    ).run(quiet=True, overwrite_output=True)
                else:
                    # Try using subprocess to call ffmpeg directly
                    try:
                        subprocess.run([
                            "ffmpeg", "-i", audio_path, 
                            "-acodec", "pcm_s16le", 
                            "-ac", "1", 
                            "-ar", "16000", 
                            "-y", output_path
                        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    except subprocess.CalledProcessError:
                        # If ffmpeg fails, just copy the file as a fallback
                        import shutil
                        shutil.copy(audio_path, output_path)
                        console.print("[yellow]Warning: Using original audio file without conversion[/yellow]")
                
                return output_path
            except Exception as e:
                console.print(f"[bold red]Error converting audio:[/bold red] {str(e)}")
                # As a last resort, just return the original file
                return audio_path
    
    def transcribe_audio(self, audio_path=None) -> None:
        """Transcribe audio file to generate lyrics with timestamps."""
        if audio_path:
            self.audio_path = audio_path
            
        if not self.audio_path:
            console.print("[yellow]No audio file selected. Please select an audio file first.[/yellow]")
            return
        
        # Convert to WAV for processing
        wav_path = self.convert_audio_to_wav(self.audio_path)
        if not wav_path:
            return
        
        # Get the base filename without extension
        base_filename = os.path.basename(self.audio_path).rsplit('.', 1)[0]
        output_json_path = self.output_dir / f"{base_filename}_lyrics.json"
        
        # Check if Whisper is available
        if not WHISPER_AVAILABLE:
            console.print("[yellow]Whisper is not available. Creating dummy lyrics for demonstration.[/yellow]")
            
            # Create dummy lyrics
            dummy_lyrics = [
                {"word": "Welcome", "start": 0.0, "end": 1.0},
                {"word": "to", "start": 1.0, "end": 1.5},
                {"word": "Automatic", "start": 1.5, "end": 2.5},
                {"word": "Lyrics", "start": 2.5, "end": 3.5},
                {"word": "Generator", "start": 3.5, "end": 4.5},
                {"word": "This", "start": 5.0, "end": 5.5},
                {"word": "is", "start": 5.5, "end": 6.0},
                {"word": "a", "start": 6.0, "end": 6.5},
                {"word": "demo", "start": 6.5, "end": 7.0},
                {"word": "mode", "start": 7.0, "end": 7.5},
                {"word": "without", "start": 8.0, "end": 8.5},
                {"word": "Whisper", "start": 8.5, "end": 9.0},
                {"word": "installed", "start": 9.0, "end": 9.5},
            ]
            
            # Process results and convert to ASCII art
            output = []
            for item in dummy_lyrics:
                # Generate ASCII art for each word
                ascii_art = generate_ascii_art(item["word"].strip())
                ascii_text = "\n".join(ascii_art)
                
                output.append({
                    "word": item["word"].strip(),
                    "ascii_art": ascii_text,
                    "start": item["start"],
                    "end": item["end"]
                })
            
            # Save to JSON
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            self.lyrics = output
            console.print(f"[bold green]Demo lyrics created![/bold green] Saved to {output_json_path}")
            return output_json_path
        
        # Load Whisper model
        with console.status("[bold green]Loading Whisper model...") as status:
            try:
                self.model = whisper.load_model("base")
                status.update("[bold green]Transcribing audio...[/bold green]")
                
                # Transcribe audio
                result = self.model.transcribe(wav_path, word_timestamps=True)
                
                # Process results and convert to ASCII art
                output = []
                for segment in result["segments"]:
                    for word in segment.get("words", []):
                        # Generate ASCII art for each word
                        ascii_art = generate_ascii_art(word["word"].strip())
                        ascii_text = "\n".join(ascii_art)
                        
                        output.append({
                            "word": word["word"].strip(),
                            "ascii_art": ascii_text,
                            "start": word["start"],
                            "end": word["end"]
                        })
                
                # Save to JSON
                with open(output_json_path, "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                
                self.lyrics = output
                console.print(f"[bold green]Transcription complete![/bold green] Saved to {output_json_path}")
                return output_json_path
            
            except Exception as e:
                console.print(f"[bold red]Error during transcription:[/bold red] {str(e)}")
                return None
    
    def play_audio_with_lyrics(self, audio_path=None) -> None:
        """Play audio file with synchronized lyrics display."""
        if audio_path:
            self.audio_path = audio_path
            
        if not self.audio_path:
            console.print("[yellow]No audio file selected. Please select an audio file first.[/yellow]")
            return
        
        # Get the base filename without extension
        base_filename = os.path.basename(self.audio_path).rsplit('.', 1)[0]
        json_path = self.output_dir / f"{base_filename}_lyrics.json"
        
        # Check if lyrics file exists
        if not os.path.exists(json_path):
            console.print(f"[yellow]Lyrics file not found for {base_filename}.[/yellow]")
            if Confirm.ask("Would you like to generate lyrics now?"):
                self.transcribe_audio()
            else:
                return
        
        # Load lyrics
        with open(json_path, encoding="utf-8") as f:
            lyrics = json.load(f)
        
        # Convert to WAV if needed
        wav_path = self.convert_audio_to_wav(self.audio_path)
        if not wav_path:
            return
        
        # Create layout for lyrics display
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main")
        )
        
        # Set up header
        layout["header"].update(Panel(
            f"[bold blue]Now Playing:[/bold blue] {os.path.basename(self.audio_path)}",
            border_style="blue"
        ))
        
        # Set up main content with lyrics
        lyrics_text = Text()
        layout["main"].update(Panel(
            Align.center(lyrics_text),
            title="[bold green]LYRICS[/bold green]",
            border_style="green"
        ))
        
        # Function to play music
        def play_music():
            if PLAYSOUND_AVAILABLE:
                try:
                    playsound(wav_path)
                except Exception as e:
                    console.print(f"[bold red]Error playing audio:[/bold red] {str(e)}")
            else:
                # Simulate audio playback duration if playsound is not available
                try:
                    # Try to get audio duration using ffmpeg
                    try:
                        if FFMPEG_AVAILABLE:
                            probe = ffmpeg.probe(wav_path)
                            duration = float(probe['format']['duration'])
                        else:
                            # Estimate duration based on lyrics end time
                            if lyrics and len(lyrics) > 0:
                                duration = max(item["end"] for item in lyrics) + 2.0
                            else:
                                duration = 30.0  # Default duration
                        
                        console.print("[yellow]Audio playback not available. Simulating playback...[/yellow]")
                        time.sleep(duration)
                    except Exception as e:
                        console.print(f"[bold red]Error simulating audio playback:[/bold red] {str(e)}")
                        # Default sleep if we can't determine duration
                        time.sleep(30)
                except KeyboardInterrupt:
                    console.print("[yellow]Playback stopped by user.[/yellow]")
        
        # Function to display lyrics with ASCII art
        def display_lyrics():
            start_time = time.time()
            current_index = 0
            current_word = ""
            buffer_words = []
            last_update_time = 0
            
            try:
                while current_index < len(lyrics):
                    now = time.time()
                    elapsed = now - start_time
                    
                    # Display words that should be shown by now
                    while current_index < len(lyrics) and lyrics[current_index]["start"] <= elapsed:
                        word = lyrics[current_index]["word"]
                        ascii_art = lyrics[current_index].get("ascii_art", "")
                        
                        # If ASCII art is not in the JSON, generate it now
                        if not ascii_art:
                            ascii_lines = generate_ascii_art(word)
                            ascii_art = "\n".join(ascii_lines)
                        
                        # Clear previous content
                        lyrics_text.plain = ""
                        
                        # Display the ASCII art
                        lyrics_text.append(ascii_art + "\n", style="bold cyan")
                        
                        # Add the plain text version below
                        lyrics_text.append("\n" + word + "\n", style="bold green")
                        
                        current_index += 1
                        time.sleep(0.1)  # Small pause between words
                    
                    time.sleep(0.05)  # Small sleep to prevent CPU hogging
            except KeyboardInterrupt:
                console.print("[yellow]Lyrics display stopped by user.[/yellow]")
        
        # Start threads
        music_thread = threading.Thread(target=play_music)
        lyrics_thread = threading.Thread(target=display_lyrics)
        
        console.print("[bold green]Starting playback with lyrics...[/bold green]")
        console.print("[italic](Press Ctrl+C to stop)[/italic]")
        
        # Display audio playback status
        if not PLAYSOUND_AVAILABLE:
            console.print("[yellow]Audio playback is disabled. Running in lyrics-only mode.[/yellow]")
        
        try:
            with Live(layout, refresh_per_second=10):
                music_thread.start()
                lyrics_thread.start()
                music_thread.join()
                lyrics_thread.join()
        except KeyboardInterrupt:
            console.print("[yellow]Playback stopped by user.[/yellow]")
    
    def run(self) -> None:
        """Run the main application loop."""
        self.display_welcome()
        
        while True:
            choice = self.show_main_menu()
            
            if choice == "1":  # Convert audio to lyrics
                if not self.audio_path:
                    console.print("[yellow]No audio file selected. Please select an audio file first.[/yellow]")
                    if Confirm.ask("Would you like to select an audio file now?"):
                        self.select_audio_file()
                        if self.audio_path:
                            self.transcribe_audio()
                else:
                    self.transcribe_audio()
            
            elif choice == "2":  # Play audio with lyrics
                self.play_audio_with_lyrics()
            
            elif choice == "3":  # Select audio file
                self.select_audio_file()
            
            elif choice == "4":  # View available audio files
                self.display_audio_files()
            
            elif choice == "5":  # Exit
                console.print("[bold blue]Thank you for using Automatic Lyrics Generator![/bold blue]")
                break
            
            # Add a separator between operations
            console.print("\n" + "─" * 50 + "\n")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Automatic Lyrics Generator")
    parser.add_argument("-f", "--file", help="Audio file to process")
    parser.add_argument("-t", "--transcribe", action="store_true", help="Transcribe the audio file")
    parser.add_argument("-p", "--play", action="store_true", help="Play audio with lyrics")
    parser.add_argument("-l", "--list", action="store_true", help="List available audio files")
    parser.add_argument("-d", "--directory", help="Base directory for the application")
    parser.add_argument("--no-audio", action="store_true", help="Run in lyrics-only mode without audio playback")
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Check if no-audio flag is set
    global PLAYSOUND_AVAILABLE
    if args.no_audio:
        PLAYSOUND_AVAILABLE = False
        print("[yellow]Running in lyrics-only mode (--no-audio flag set)[/yellow]")
    
    # Initialize the application
    app = LyricGenerator(args.directory)
    
    # Process command line arguments
    if args.list:
        app.display_audio_files()
        return
    
    if args.file:
        # Check if the file exists
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[bold red]Error:[/bold red] File {args.file} not found.")
            return
        
        # Set the audio path
        app.audio_path = str(file_path)
        
        # Transcribe or play based on arguments
        if args.transcribe:
            app.transcribe_audio()
        elif args.play:
            app.play_audio_with_lyrics()
        else:
            # If no specific action is requested, run the interactive mode
            app.run()
    else:
        # No file specified, run the interactive mode
        app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[bold yellow]Program terminated by user.[/bold yellow]")
    except Exception as e:
        print(f"\n[bold red]An error occurred:[/bold red] {str(e)}")
        import traceback
        traceback.print_exc()