import pyaudio
import wave
from openai import OpenAI
import time
import os

class SpeechToText:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)
        
        # Audio recording parameters
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.record_seconds = 3 
        
        self.audio = pyaudio.PyAudio()
    
    def record_audio(self):
        print(f"\nRecording for {self.record_seconds} seconds...")
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        
        # Record audio
        for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
            
            # Show progress
            if i % int(self.rate / (self.chunk * 2)) == 0:  # Update twice per second
                seconds_left = self.record_seconds - (i * self.chunk / self.rate)
                print(f"Recording... {seconds_left:.1f} seconds left", end='\r')
        
        print("\nFinished!")
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        
        return frames
    
    def save_audio(self, frames, filename="temp.wav"):
        """Save recorded audio to WAV file"""
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
    
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
        """Function to handle recording and transcription"""
        # Record audio
        frames = self.record_audio()
        
        # Save audio
        temp_file = "temp_recording.wav"
        self.save_audio(frames, temp_file)
        
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

