import sounddevice as sd
import numpy as np
import wave
from pathlib import Path
from openai import OpenAI
import time
import os

class SpeechToText:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)
        
        # Audio recording parameters
        self.channels = 1
        self.rate = 44100
        self.record_seconds = 3 
    
    def record_audio(self):
        """Record audio for a given duration using sounddevice"""
        print(f"\nRecording for {self.record_seconds} seconds...")
        audio = sd.rec(int(self.record_seconds * self.rate), samplerate=self.rate, channels=self.channels, dtype='int16')
        sd.wait()  # Wait until the recording is finished
        print("Recording finished.")
        return audio

    def save_audio(self, audio, filename="temp.wav"):
        """Save recorded audio to a WAV file"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.rate)
            wf.writeframes(audio.tobytes())
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio file using OpenAI Whisper API with automatic language detection"""
        try:
            with open(audio_file, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                )
            return transcription.text
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None
    
    def record_and_transcribe(self):
        """Main function to handle recording and transcription"""
        # Record audio
        audio = self.record_audio()
        
        # Save audio
        temp_file = "temp_recording.wav"
        self.save_audio(audio, temp_file)
        
        # Transcribe
        print("Processing transcription...")
        text = self.transcribe_audio(temp_file)
        if text:
            print(f"Transcription: {text}")
            # Save transcription with timestamp
            with open("transcriptions.txt", "a", encoding='utf-8') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: {text}\n")
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
# Example usage with OSC integration
def handle_osc_command(stt_instance):
    """Trigger recording and transcription on receiving OSC command"""
    stt_instance.record_and_transcribe()

if __name__ == "__main__":
    stt = SpeechToText()
    try:
        # Replace this line with the OSC setup code that triggers handle_osc_command
        handle_osc_command(stt)  # This should be triggered by OSC in your actual setup
    except KeyboardInterrupt:
        pass
    finally:
        print("\nRecording session ended.")
