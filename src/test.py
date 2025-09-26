#!/usr/bin/env python3
"""
Test script for the Automatic Lyrics Generator application.
This script verifies that all dependencies are installed correctly.
"""

import sys
import importlib.util

def check_dependency(package_name):
    """Check if a Python package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible."""
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def main():
    """Run tests to verify the application setup."""
    # List of required packages
    required_packages = [
        'rich',
        'whisper',
        'ffmpeg',
        'playsound',
        'pydub'
    ]
    
    print("Testing Automatic Lyrics Generator setup...")
    print("\nChecking Python dependencies:")
    
    all_packages_installed = True
    for package in required_packages:
        is_installed = check_dependency(package)
        status = "✓ Installed" if is_installed else "✗ Not installed"
        print(f"  {package}: {status}")
        if not is_installed:
            all_packages_installed = False
    
    print("\nChecking system dependencies:")
    ffmpeg_installed = check_ffmpeg()
    print(f"  ffmpeg: {'✓ Installed' if ffmpeg_installed else '✗ Not installed'}")
    
    print("\nChecking project structure:")
    import os
    
    # Define expected directories
    expected_dirs = ['audio', 'output', 'src', 'temp']
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    all_dirs_exist = True
    for directory in expected_dirs:
        dir_path = os.path.join(project_root, directory)
        exists = os.path.isdir(dir_path)
        print(f"  {directory}/: {'✓ Exists' if exists else '✗ Missing'}")
        if not exists:
            all_dirs_exist = False
    
    # Check if sample audio exists
    sample_audio = os.path.join(project_root, 'audio', 'laguv2.mp3')
    audio_exists = os.path.isfile(sample_audio)
    print(f"  Sample audio: {'✓ Exists' if audio_exists else '✗ Missing'}")
    
    # Overall status
    print("\nTest results:")
    if all_packages_installed and ffmpeg_installed and all_dirs_exist and audio_exists:
        print("✓ All tests passed! The application should work correctly.")
    else:
        print("✗ Some tests failed. Please check the issues above.")
    
    return 0 if (all_packages_installed and ffmpeg_installed and all_dirs_exist and audio_exists) else 1

if __name__ == "__main__":
    sys.exit(main())