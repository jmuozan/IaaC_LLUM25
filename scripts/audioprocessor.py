import os
import soundfile as sf
import sounddevice as sd  
import numpy as np

class AudioProcessor:
    def __init__(self, rate=44100, channels=1, record_seconds=5):
        self.rate = rate
        self.channels = channels
        self.record_seconds = record_seconds

    def record_audio(self):
        print("Recording audio...")
        audio_data = sd.rec(int(self.record_seconds * self.rate), samplerate=self.rate, channels=self.channels)
        sd.wait()
        return audio_data

    def save_audio(self, audio_data, filename):
        sf.write(filename, audio_data, self.rate)
        return filename

    def merge_audio_files(self, audio_files, output_filename="static/audio/combined_audio.wav"):
        # Ensure the directory exists
        output_directory = os.path.dirname(output_filename)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Combine the audio data
        combined_audio = np.concatenate([sf.read(f)[0] for f in audio_files])
        
        # Save the combined audio
        sf.write(output_filename, combined_audio, self.rate)
        print(f"Merged audio saved as {output_filename}")
        return output_filename
