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

# Try to import required packages with fallbacks
try:
    import whisper
except ImportError:
    print("Whisper is not installed. Please run the install.sh script first.")
    sys.exit(1)

try:
    import ffmpeg
except ImportError:
    print("ffmpeg-python is not installed. Please run the install.sh script first.")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
except ImportError:
    print("Rich is not installed. Please run the install.sh script first.")
    sys.exit(1)

try:
    from playsound import playsound
except ImportError:
    try:
        # Try to use our fallback module
        from fallback import playsound
        print("Using fallback playsound module with ffplay")
    except ImportError:
        print("Audio playback libraries are not installed. Please run the install.sh script first.")
        sys.exit(1)

try:
    from pydub import AudioSegment
except ImportError:
    print("Pydub is not installed. Please run the install.sh script first.")
    sys.exit(1)

# Initialize Rich console
console = Console()

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
        console.print(Panel.fit(
            "[bold blue]Automatic Lyrics Generator[/bold blue]\n"
            "[italic]Generate and display lyrics from audio files in real-time[/italic]",
            border_style="blue",
            padding=(1, 10)
        ))
        
        console.print("\n[bold]Features:[/bold]")
        features = Table(show_header=False, box=None)
        features.add_column(style="green")
        features.add_row("• Convert audio files to text with timestamps")
        features.add_row("• Play audio with synchronized lyrics display")
        features.add_row("• Support for various audio formats")
        features.add_row("• Save lyrics to JSON format")
        console.print(features)
        console.print()
    
    def show_main_menu(self) -> str:
        """Display the main menu and return the selected option."""
        console.print("[bold]Main Menu[/bold]", style="blue")
        
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
                # Use ffmpeg to convert to WAV with proper settings for Whisper
                ffmpeg.input(audio_path).output(
                    output_path, 
                    acodec='pcm_s16le',
                    ac=1,  # mono
                    ar=16000  # 16kHz sample rate
                ).run(quiet=True, overwrite_output=True)
                return output_path
            except Exception as e:
                console.print(f"[bold red]Error converting audio:[/bold red] {str(e)}")
                return None
    
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
        
        # Load Whisper model
        with console.status("[bold green]Loading Whisper model...") as status:
            try:
                self.model = whisper.load_model("base")
                status.update("[bold green]Transcribing audio...[/bold green]")
                
                # Transcribe audio
                result = self.model.transcribe(wav_path, word_timestamps=True)
                
                # Process results
                output = []
                for segment in result["segments"]:
                    for word in segment["words"]:
                        output.append({
                            "word": word["word"].strip(),
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
        layout["main"].update(Panel(lyrics_text, title="Lyrics", border_style="green"))
        
        # Function to play music
        def play_music():
            try:
                playsound(wav_path)
            except Exception as e:
                console.print(f"[bold red]Error playing audio:[/bold red] {str(e)}")
        
        # Function to display lyrics
        def display_lyrics():
            start_time = time.time()
            current_index = 0
            
            while current_index < len(lyrics):
                now = time.time()
                elapsed = now - start_time
                
                # Display words that should be shown by now
                while current_index < len(lyrics) and lyrics[current_index]["start"] <= elapsed:
                    word = lyrics[current_index]["word"]
                    lyrics_text.append(word + " ", style="bold white")
                    
                    # Keep only the last few lines visible
                    if len(lyrics_text.plain) > 500:
                        lyrics_text.plain = lyrics_text.plain[-500:]
                    
                    current_index += 1
                
                time.sleep(0.05)  # Small sleep to prevent CPU hogging
        
        # Start threads
        music_thread = threading.Thread(target=play_music)
        lyrics_thread = threading.Thread(target=display_lyrics)
        
        console.print("[bold green]Starting playback with lyrics...[/bold green]")
        console.print("[italic](Press Ctrl+C to stop)[/italic]")
        
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
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
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
        console.print("\n[bold yellow]Program terminated by user.[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]An error occurred:[/bold red] {str(e)}")
        console.print_exception()