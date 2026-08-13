import whisper
import tempfile
import os
from pathlib import Path
model = whisper.load_model("base")

class audioExtract:
   def extract_audio_text(self, file_content: bytes, filename: str):

    extension = Path(filename).suffix.lower()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=extension
    ) as temp_file:

        temp_file.write(file_content)
        temp_path = temp_file.name

    try:
        result = model.transcribe(
            temp_path,
            fp16=False
        )

        chunks = []

        for segment in result["segments"]:
            chunks.append({
                "start_time": segment["start"],
                "end_time": segment["end"],
                "text": segment["text"].strip()
            })

        return chunks

    finally:
        os.remove(temp_path)
audio_extract = audioExtract()