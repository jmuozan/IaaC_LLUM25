import sounddevice as sd
import soundfile as sf
import numpy as np

class AudioProcessor:
    def __init__(self, rate=44100, channels=1, record_seconds=5):
        self.rate = rate
        self.channels = channels
        self.record_seconds = record_seconds

    def record_audio(self):
        """Record audio and return it as a numpy array."""
        print(f"Recording for {self.record_seconds} seconds...")
        audio_data = sd.rec(int(self.record_seconds * self.rate), samplerate=self.rate, channels=self.channels)
        sd.wait()  # Wait until recording is finished
        print("Recording complete.")
        return audio_data

    def save_audio(self, audio_data, filename="temp.wav"):
        """Save audio data to a WAV file using soundfile."""
        sf.write(filename, audio_data, self.rate)
        print(f"Audio saved as {filename}")


#to test audio processor
#audio_processor = AudioProcessor()
#audio_data = audio_processor.record_audio()
#audio_processor.save_audio(audio_data, "test_recording.wav")
