import os
import json
import whisper
import ffmpeg

ffmpeg.input("laguv2.mp3").output("lagu.wav", ac=1, ar=16000).run()
model = whisper.load_model("base")
result = model.transcribe("lagu.wav", word_timestamps=True)

output = []
for segment in result["segments"]:
    for word in segment["words"]:
        output.append({
            "word": word["word"].strip(),
            "start": word["start"],
            "end": word["end"]
        })
os.makedirs("output", exist_ok=True)

with open("output/lirik.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
