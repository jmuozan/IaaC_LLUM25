from scripts.audioprocessor import AudioProcessor
from scripts.new_audioprocessor import NewAudioProcessor
from scripts.transcribe_audio import transcribe_audio
import requests
import multiprocessing
import time
import os
import json
import subprocess
from scripts.image_manager import update_image_on_web
from scripts.history_manager import update_and_get_history
import sys

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ensure directories exist
audio_dir = os.path.join("scripts", "static", "audio")
os.makedirs(audio_dir, exist_ok=True)

# Path to the shared batch file
# BATCH_FILE = os.path.join("scripts", "batch_transcriptions.json")


# URLs
IMAGE_GENERATION_URL = "http://127.0.0.1:8003/generate-image"
WEB_ADD_SENTENCE_URL = "http://127.0.0.1:8001/add-sentence"


# Ensure the batch file exists
''''if not os.path.exists(BATCH_FILE):
    with open(BATCH_FILE, "w") as f:
        json.dump([], f)'''


def start_fastapi_server():
    """Start FastAPI server as a subprocess."""
    process = subprocess.Popen(
        ["uvicorn", "scripts.app_display:app", "--host", "127.0.0.1", "--port", "8002"]
    )
    time.sleep(3)  # Wait for the server to initialize
    return process


def send_transcription_to_web(transcription):
    """Send transcription to the web app."""
    data = {"sentence": transcription}
    try:
        response = requests.post(WEB_ADD_SENTENCE_URL, data=data)
        response.raise_for_status()
        print(f"Sent transcription to web: {transcription}")
    except Exception as e:
        print(f"Failed to send transcription: {e}")

def send_image_generation_request(prompt):
    """Send the prompt to the image manager to generate an image."""
    data = {"prompt": prompt}
    try:
        response = requests.post(IMAGE_GENERATION_URL, json=data)
        response.raise_for_status()
        print(f"[INFO] Image generation triggered for prompt: {prompt}")
    except Exception as e:
        print(f"[ERROR] Failed to trigger image generation: {e}")


'''def write_to_batch_file(transcriptions):
    """Write transcription batch to a shared file."""
    try:
        with open(BATCH_FILE, "r+") as f:
            batch = json.load(f)
            batch.extend(transcriptions)
            f.seek(0)
            json.dump(batch, f)
            f.truncate()
        print(f"Batch written to {BATCH_FILE}: {transcriptions}")
    except Exception as e:
        print(f"Failed to write to batch file: {e}")'''


def process_audio_and_transcriptions():
    """Main processing loop for audio transcription."""
    audio_processor = AudioProcessor()
    #audio_processor = NewAudioProcessor()
    transcriptions = []

    try:
       while True:
        print("Recording audio...")
        audio_path = audio_processor.record_and_save(audio_dir)

        # Add RMS filtering directly here
        if audio_processor.is_silent(audio_path):
            print("[INFO] Audio is silent. Ignoring this recording.")
            continue
    
        # Skip if the audio didn't pass the filters
        '''if audio_path is None:
            print("[INFO] Skipping invalid audio.")
            continue'''

        print(f"[INFO] Transcribing audio: {audio_path}")
        transcription = transcribe_audio(audio_path).strip()

        if not transcription:
            print("[INFO] Empty transcription. Skipping.")
            continue

        print(f"[INFO] Transcription: {transcription}")
        transcriptions.append(transcription)
        send_transcription_to_web(transcription)  # Send transcription to the web

        # Update history.txt and get the trimmed history
        trimmed_history = update_and_get_history([transcription])
        print(f"[DEBUG] Updated history.txt: {trimmed_history}")

        # If 3 transcriptions are ready, generate an image
        if len(transcriptions) % 3 == 0:
            prompt = " ".join(trimmed_history[-3:])
            print(f"[INFO] Generating image with prompt: {prompt}")
            send_image_generation_request(prompt)
            
        time.sleep(2)  # Add delay to avoid rapid polling

    except KeyboardInterrupt:
        print("Recording interrupted. Exiting program...")


if __name__ == "__main__":
    # Start FastAPI server in a separate process
    fastapi_process = multiprocessing.Process(target=start_fastapi_server)
    fastapi_process.start()

    # Wait for FastAPI server to start
    time.sleep(3)

    # Start the main processing loop
    process_audio_and_transcriptions()

    # Ensure FastAPI server is terminated on exit
    fastapi_process.terminate()
