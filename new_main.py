import asyncio
from collections import deque
from scripts.audioprocessor import AudioProcessor
from scripts.transcribe_audio import transcribe_audio
from scripts.history_manager import append_to_history, add_sentences_in_progress, finalize_sentences 
import requests
import websockets
import json

# Constants
AUDIO_DIR = "scripts/static/audio"
WEBSOCKET_URL = "ws://127.0.0.1:8001/ws"
IMAGE_GENERATION_URL = "http://127.0.0.1:8003/generate-image"
UPDATE_SENTENCES_URL = "http://127.0.0.1:8001/update-sentences"
UPDATE_IMAGE_URL = "http://127.0.0.1:8001/update-image"
PACKAGE_SIZE = 3  # Number of sentences per image generation
SENTENCES_FILE = "scripts/sentences.json"
# Queue to hold transcriptions for batching
transcription_queue = deque(maxlen=PACKAGE_SIZE)

# Graceful shutdown flag
shutdown_flag = False

def update_sentence_status(sentences, status):
    """Update the statuses of specific sentences in `sentences.json`."""
    try:
        with open(SENTENCES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Update the status of the specified sentences
        for sentence in data:
            if sentence["text"] in sentences:
                sentence["status"] = status

        # Remove the oldest "done" sentences if there are more than 3
        done_sentences = [s for s in data if s["status"] == "done"]
        if len(done_sentences) > 3:
            data = [s for s in data if s not in done_sentences[:-3]]

        with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"[INFO] Updated statuses for: {sentences}")
    except Exception as e:
        print(f"[ERROR] Failed to update sentence statuses: {e}")

# Transcription processing
async def handle_audio_processing(websocket):
    """Continuously process audio and send transcriptions."""
    audio_processor = AudioProcessor()

    while not shutdown_flag:
        try:
            # Record audio
            audio_path = await asyncio.to_thread(audio_processor.record_and_save, AUDIO_DIR)

            # Skip silent audio
            if await asyncio.to_thread(audio_processor.is_silent, audio_path):
                continue

            # Transcribe the audio
            transcription = await asyncio.to_thread(transcribe_audio, audio_path)
            if not transcription.strip():
                continue

            # Append transcription to queue and history
            transcription_queue.append(transcription.strip())
            append_to_history([transcription.strip()])
            updated_sentences = add_sentences_in_progress([transcription.strip()])

            # Notify WebSocket clients
            requests.post(UPDATE_SENTENCES_URL, json=updated_sentences)
            # If we have enough sentences in the queue, generate an image
            if len(transcription_queue) == PACKAGE_SIZE:
                await generate_image(websocket)

            await asyncio.sleep(1)  # Optional delay
        except asyncio.CancelledError:
            print("[INFO] Audio processing task canceled.")
            break
        except Exception as e:
            print(f"[ERROR] Audio processing error: {e}")

# Image generation process
async def generate_image(websocket):
    """Generate an image using the top 3 sentences."""
    try:
        # Prepare the prompt from the first PACKAGE_SIZE sentences
        package = list(transcription_queue)
        prompt = " ".join(package)

        # Generate the image
        response = requests.post(IMAGE_GENERATION_URL, json={"prompt": prompt})
        response.raise_for_status()
        image_path = response.json().get("image_path")

         # Update sentences.json statuses
        update_sentence_status(package, "done")  # Mark the package as "done"
        requests.post(UPDATE_IMAGE_URL, json={"image_path": image_path})
        updated_sentences = finalize_sentences()
        requests.post(UPDATE_SENTENCES_URL, json=updated_sentences)


        # Clear the processed sentences from the queue
        transcription_queue.clear()

    except asyncio.CancelledError:
        print("[INFO] Image generation task canceled.")
        return
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")

async def main():
    """Main function to coordinate transcription and image generation."""
    global shutdown_flag
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("[INFO] Connected to WebSocket")
            await handle_audio_processing(websocket)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[ERROR] WebSocket closed: {e}")
    except asyncio.CancelledError:
        print("[INFO] Main task canceled.")
    finally:
        shutdown_flag = True  # Signal shutdown to all tasks
        print("[INFO] Shutting down gracefully...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[INFO] KeyboardInterrupt received. Exiting...")