import os
from scripts.audioprocessor import AudioProcessor
from scripts.transcribe_audio import transcribe_audio

def main():
    # Step 1: Initialize AudioProcessor
    audio_processor = AudioProcessor()
    transcriptions = []

    # Step 2: Record and transcribe three times
    for i in range(1, 4):
        print(f"\nRecording {i} of 3...")
        audio_data = audio_processor.record_audio()
        filename = f"recording_{i}.wav"
        audio_processor.save_audio(audio_data, filename)

        # Transcribe the audio and store the result
        transcription = transcribe_audio(filename)
        if transcription:
            transcriptions.append(transcription)
            print(f"Transcription {i}: {transcription}")
        
        # Optional: Clean up the audio file after transcription
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Deleted temporary file: {filename}")

    # Step 3: Print all transcriptions at the end
    print("\nAll Transcriptions:")
    for i, transcription in enumerate(transcriptions, 1):
        print(f"{i}: {transcription}")

if __name__ == "__main__":
    main()
