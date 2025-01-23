import asyncio
from collections import deque
from scripts.audioprocessor import AudioProcessor
from scripts.transcribe_audio import transcribe_audio
from scripts.history_manager import append_to_history, add_sentences_in_progress, finalize_sentences 
from scripts.supabase_test import upload_image_and_save_to_db
from scripts.osc_receiver import start_osc_receiver
import requests
import websockets
import json
import os

# Constants
AUDIO_DIR = "scripts/static/audio"
WEBSOCKET_URL = "ws://127.0.0.1:8001/ws"
IMAGE_GENERATION_URL = "http://127.0.0.1:8003/generate-image"
UPDATE_SENTENCES_URL = "http://127.0.0.1:8001/update-sentences"
UPDATE_IMAGE_URL = "http://127.0.0.1:8001/update-image"
CURRENT_QUESTION_URL = "http://127.0.0.1:8001/current-question"
UPDATE_STATE_URL = "http://127.0.0.1:8001/state-update"
PACKAGE_SIZE = 3  # Number of sentences per image generation
SENTENCES_FILE = "scripts/sentences.json"

# Add these definitions
OSC_HOST = "0.0.0.0"  # Address the OSC receiver will bind to
OSC_PORT = 8009       # Port the OSC receiver will listen on

# Add new constant
UPDATE_COUNTER_URL = "http://127.0.0.1:8001/update-counter"

# Queue to hold transcriptions for batching
transcription_queue = deque(maxlen=PACKAGE_SIZE)
osc_queue = asyncio.Queue()
is_recording = False
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

async def update_state(state):
    """Send state update to the interface."""
    try:
        response = requests.post(UPDATE_STATE_URL, json={"state": state})
        response.raise_for_status()
        print(f"[INFO] State updated to: {state}")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to update state: {e}")

# Add new function to update counter
async def update_counter(count):
    """Send counter update to the interface."""
    try:
        response = requests.post(UPDATE_COUNTER_URL, json={"count": count})
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to update counter: {e}")

# Modify the handle_osc_messages function
async def handle_osc_messages(websocket):
    """Handle OSC messages, manage recording, and process transcription."""
    global is_recording
    audio_processor = AudioProcessor()
    # Transcription processing

    while not shutdown_flag:
        try:
            # Check for new OSC messages
            if not osc_queue.empty():
                message = await osc_queue.get()

                if message == "record":
                    is_recording = True
                    print("[INFO] Recording triggered...")
                    # Notify the interface about the recording state

                elif message == "pause":
                    print("[INFO] Pausing recording...")
                    await update_state("idle")
                    is_recording = False

            if is_recording:
                print("[INFO] Recording...")
                # Keep recording until 3 sentences are transcribed
                try:
                    await update_state("recording")
                    # Record audio
                    audio_path = await asyncio.to_thread(audio_processor.record_and_save, AUDIO_DIR)

                    # Check if the audio is silent
                    if await asyncio.to_thread(audio_processor.is_silent, audio_path):
                        await update_state("idle")
                        # print("[WARNING] Silent audio detected. Retrying...")
                        continue

                    await update_state("transcribing")
                    is_recording = False

                    # Transcribe audio
                    transcription = await asyncio.to_thread(transcribe_audio, audio_path)
                    if not transcription.strip():
                        # print("[WARNING] Empty transcription. Retrying...")
                        await update_state("idle")
                        continue

                    # Process valid transcription
                    transcription_queue.append(transcription.strip())
                    append_to_history([transcription.strip()])
                    await update_state("idle")
                    updated_sentences = add_sentences_in_progress([transcription.strip()])
                    requests.post(UPDATE_SENTENCES_URL, json=updated_sentences)
                    # print(f"[INFO] Collected {len(transcription_queue)} transcriptions.")

                    # Update counter
                    await update_counter(len(transcription_queue))

                    # Proceed to image generation if 3 transcriptions are collected
                    if len(transcription_queue) == PACKAGE_SIZE:
                        await generate_image(websocket, transcription_queue)
                        # Reset counter after image generation
                        await update_counter(0)
                        transcription_queue.clear()

                except Exception as e:
                    print(f"[ERROR] Error during recording or transcription: {e}")
                    continue  # Retry recording in case of failure

            # After completing a loop, re-check OSC message status
            await asyncio.sleep(1)  # Short pause to avoid busy waiting

        except Exception as e:
            print(f"[ERROR] Error handling OSC message: {e}")
                

async def fetch_current_question():
    """Fetch the current question from the app server."""
    try:
        response = requests.get(CURRENT_QUESTION_URL)
        response.raise_for_status()
        question_data = response.json()
        current_question = question_data.get("current_question", "How will living in cities look like in the future ?")
        # print(f"[INFO] Current question fetched: {current_question}")
        return current_question
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch current question: {e}")
        return "How will living in cities look like in the future ?"
    
# Image generation process
async def generate_image(websocket, transcription_queue):
    """Generate an image using the top 3 sentences."""
    try:
        # Prepare the prompt from the first PACKAGE_SIZE sentences
        package = list(transcription_queue)
        prompt = " ".join(package)

        current_question = await fetch_current_question()
        print(f"[DEBUG] Question used in Supabase upload: {current_question}")
        await update_state("image_processing")

        # Generate the image
        response = requests.post(IMAGE_GENERATION_URL, json={"prompt": prompt, "question": current_question})
        response.raise_for_status()
        image_path = response.json().get("image_path")
        # print(image_path)
        # Map web path to local file path
        local_image_path = os.path.join("scripts", image_path.lstrip("/"))  # Convert to local path
        # print(f"[INFO] Local image path: {local_image_path}")#
        await update_state("image_generated")

         # Update sentences.json statuses
        update_sentence_status(package, "done")  # Mark the package as "done"
        requests.post(UPDATE_IMAGE_URL, json={"image_path": image_path})
        updated_sentences = finalize_sentences()
        requests.post(UPDATE_SENTENCES_URL, json=updated_sentences)
        await update_state("image_uploading")

        # Upload the image and save to Supabase
        upload_image_and_save_to_db(local_image_path, prompt, current_question)

        await update_state("idle")
        


        # Clear the processed sentences from the queue
        transcription_queue.clear()

    except asyncio.CancelledError:
        print("[INFO] Image generation task canceled.")
        return
    except Exception as e:
        print(f"[ERROR] Image generation failed: {e}")

async def main():
    """Main function to coordinate OSC, audio, and WebSocket communication."""
    global shutdown_flag

    osc_transport, osc_protocol = await start_osc_receiver(osc_queue, host=OSC_HOST, port=OSC_PORT)

    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("[INFO] Connected to WebSocket")
            await asyncio.gather(handle_osc_messages(websocket))
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        shutdown_flag = True
        osc_transport.close()
        print("[INFO] Shutting down gracefully...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[INFO] KeyboardInterrupt received. Exiting...")