import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(audio_file):
    """Transcribe audio file using Whisper."""
    try:
        with open(audio_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=file,
            )
        print(f"Transcription: {transcription.text}")
        return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


#transcription = transcribe_audio("test_recording.wav")
#print(transcription)
