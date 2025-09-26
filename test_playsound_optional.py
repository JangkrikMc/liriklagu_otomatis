#!/usr/bin/env python3
"""
Test script to verify that playsound is optional
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Mock the required modules
sys.modules['whisper'] = type('MockWhisper', (), {})
sys.modules['ffmpeg'] = type('MockFFmpeg', (), {})
sys.modules['rich.console'] = type('MockRich', (), {'Console': type('MockConsole', (), {'print': lambda *args, **kwargs: None})})
sys.modules['rich.panel'] = type('MockRichPanel', (), {'Panel': type('MockPanel', (), {'fit': lambda *args, **kwargs: None})})
sys.modules['rich.prompt'] = type('MockRichPrompt', (), {
    'Prompt': type('MockPrompt', (), {'ask': lambda *args, **kwargs: None}),
    'Confirm': type('MockConfirm', (), {'ask': lambda *args, **kwargs: None})
})
sys.modules['rich.progress'] = type('MockRichProgress', (), {
    'Progress': type('MockProgress', (), {}),
    'SpinnerColumn': type('MockSpinnerColumn', (), {}),
    'TextColumn': type('MockTextColumn', (), {}),
    'BarColumn': type('MockBarColumn', (), {}),
    'TimeElapsedColumn': type('MockTimeElapsedColumn', (), {})
})
sys.modules['rich.table'] = type('MockRichTable', (), {'Table': type('MockTable', (), {
    'add_column': lambda *args, **kwargs: None,
    'add_row': lambda *args, **kwargs: None
})})
sys.modules['rich.text'] = type('MockRichText', (), {'Text': type('MockText', (), {
    'append': lambda *args, **kwargs: None,
    'plain': ''
})})
sys.modules['rich.layout'] = type('MockRichLayout', (), {'Layout': type('MockLayout', (), {
    'split': lambda *args, **kwargs: None,
    'update': lambda *args, **kwargs: None,
    '__getitem__': lambda *args, **kwargs: type('MockLayoutItem', (), {'update': lambda *args, **kwargs: None})()
})})
sys.modules['rich.live'] = type('MockRichLive', (), {'Live': type('MockLive', (), {
    '__enter__': lambda *args, **kwargs: None,
    '__exit__': lambda *args, **kwargs: None
})})
sys.modules['rich.align'] = type('MockRichAlign', (), {'Align': type('MockAlign', (), {
    'center': lambda *args, **kwargs: None
})})
sys.modules['rich.box'] = type('MockRichBox', (), {'Box': type('MockBox', (), {})})
sys.modules['pydub'] = type('MockPydub', (), {'AudioSegment': type('MockAudioSegment', (), {})})

# Now try to import the main module
try:
    from main import PLAYSOUND_AVAILABLE, playsound
    
    print("Successfully imported main module")
    print(f"PLAYSOUND_AVAILABLE = {PLAYSOUND_AVAILABLE}")
    
    # Test the playsound function
    try:
        playsound("nonexistent_file.wav")
        print("playsound function executed without errors (dummy function)")
    except FileNotFoundError:
        print("playsound function raised FileNotFoundError (real function)")
    except Exception as e:
        print(f"playsound function raised an unexpected error: {e}")
    
    print("Test completed successfully!")
except ImportError as e:
    print(f"Failed to import main module: {e}")
except Exception as e:
    print(f"An error occurred: {e}")