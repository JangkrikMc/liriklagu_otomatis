# Fallback playsound module
def playsound(sound_file, block=True):
    """
    Fallback playsound function that uses ffplay from ffmpeg
    """
    import subprocess
    import os
    
    if not os.path.exists(sound_file):
        raise FileNotFoundError(f"Sound file not found: {sound_file}")
    
    try:
        # Use ffplay from ffmpeg to play the sound
        cmd = ["ffplay", "-nodisp", "-autoexit", "-hide_banner", "-loglevel", "quiet", sound_file]
        if block:
            subprocess.call(cmd)
        else:
            subprocess.Popen(cmd)
        return True
    except Exception as e:
        print(f"Error playing sound: {e}")
        return False