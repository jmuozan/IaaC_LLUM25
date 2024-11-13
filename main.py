from scripts.audioprocessor import AudioProcessor
from scripts.transcribe_audio import transcribe_audio
from scripts.image_generator import generate_image
from scripts.history_manager import update_and_get_history

def main():
    # Initialize components
    audio_processor = AudioProcessor()
    transcriptions = []
    audio_files = []

    # Step 1: Record and transcribe 3 times
    for i in range(3):
        audio_data = audio_processor.record_audio()
        audio_filename = f"recording_{i+1}.wav"
        audio_processor.save_audio(audio_data, audio_filename)
        audio_files.append(audio_filename)

        # Transcribe audio
        transcription = transcribe_audio(audio_filename)
        transcriptions.append(transcription)
        print(f"Transcription {i+1}: {transcription}")

    # Step 2: Store transcriptions in history.txt and prepare image prompt
    combined_text = " ".join(transcriptions)
    history = update_and_get_history(transcriptions)

    # Step 3: Generate image based on combined history
    prompt = "This is a collaborative image based on: " + ". ".join(history)
    image_path = generate_image(prompt)

    # Step 4: Merge audio files
    merged_audio_path = audio_processor.merge_audio_files(audio_files)

    print(f"Image saved at: {image_path}")
    print(f"Combined audio saved at: {merged_audio_path}")

if __name__ == "__main__":
    main()
