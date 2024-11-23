from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(audio_file):
    """Transcribe an audio file using OpenAI's Whisper."""
    try:
        print(f"[DEBUG] Transcribing audio file: {audio_file}")
        with open(audio_file, "rb") as file:
            response = client.audio.transcriptions.create(model="whisper-1", file=file)
        transcription = response.text.strip()
        print(f"[DEBUG] Transcription result: {transcription}")
        return transcription
    except Exception as e:
        print(f"[ERROR] Failed to transcribe audio: {e}")
        return ""