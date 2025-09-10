import json
import time
import threading
from playsound import playsound

def play_music():
    playsound("lagu.wav")

def tampil_lirik():
    with open("output/lirik.json", encoding="utf-8") as f:
        lirik = json.load(f)

    start_time = time.time()
    for kata in lirik:
        now = time.time()
        delay = kata["start"] - (now - start_time)
        if delay > 0:
            time.sleep(delay)
        print(kata["word"], end=' ', flush=True)

t1 = threading.Thread(target=play_music)
t2 = threading.Thread(target=tampil_lirik)

t1.start()
t2.start()
t1.join()
t2.join()




