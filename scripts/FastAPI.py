from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from scripts.audioprocessor import AudioProcessor
from scripts.transcribe_audio import transcribe_audio
from scripts.image_generator import generate_image
from scripts.history_manager import update_and_get_history
import os

app = FastAPI()

audio_processor = AudioProcessor()
audio_files = []
transcriptions = []

@app.get("/")
async def get_interface():
    """Serve the HTML interface."""
    return FileResponse("templates/index.html")

@app.post("/trigger_process")
async def trigger_process(background_tasks: BackgroundTasks):
    """Trigger the process to record, transcribe, merge audio, and generate image."""
    background_tasks.add_task(process_transcriptions)
    return {"message": "Processing started"}

@app.get("/latest_image")
async def get_latest_image():
    """Return the latest generated image."""
    image_path = "static/Generated_Images/generated_image.jpeg"
    return FileResponse(image_path)

@app.get("/latest_audio")
async def get_latest_audio():
    """Return the latest combined audio."""
    audio_path = "static/audio/combined_audio.wav"
    return FileResponse(audio_path)

def process_transcriptions():
    """Record 3 audios, transcribe, store history, generate image, and merge audio."""
    global audio_files, transcriptions
    audio_files = []
    transcriptions = []

    # Record and transcribe three times
    for i in range(3):
        audio_data = audio_processor.record_audio()
        audio_filename = f"recording_{i+1}.wav"
        audio_processor.save_audio(audio_data, audio_filename)
        audio_files.append(audio_filename)

        transcription = transcribe_audio(audio_filename)
        transcriptions.append(transcription)
        print(f"Transcription {i+1}: {transcription}")

    # Update history and generate image
    combined_text = " ".join(transcriptions)
    history = update_and_get_history(transcriptions)
    prompt = "This is a collaborative image based on: " + ". ".join(history)
    generate_image(prompt)

    # Merge audio files
    audio_processor.merge_audio_files(audio_files)



# Main entry point to run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)