from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_transcription_data(transcription_text, audio_url, image_url):
    data = {
        "transcription": transcription_text,
        "audio_url": audio_url,
        "image_url": image_url
    }
    supabase.table("transcriptions").insert(data).execute()

