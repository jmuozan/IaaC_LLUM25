import os
import soundfile as sf
import sounddevice as sd  
import numpy as np
import time  # Import time module

class AudioProcessor:
    def __init__(self, rate=44100, channels=1, record_seconds=8, silent_threshold=0.01):
        self.rate = rate
        self.channels = channels
        self.record_seconds = record_seconds
        self.silent_threshold = silent_threshold

    def record_audio(self):
        print("Recording audio...")
        audio_data = sd.rec(int(self.record_seconds * self.rate), samplerate=self.rate, channels=self.channels)
        sd.wait()
        return audio_data

    def save_audio(self, audio_data, filename):
        sf.write(filename, audio_data, self.rate)
        return filename
    
    def is_silent(self, audio_path):
        """Check if the audio file is silent based on RMS threshold."""
        try:
            audio_data, _ = sf.read(audio_path)  # Load the audio file
            rms = np.sqrt(np.mean(audio_data**2))  # Calculate RMS
            print(f"[DEBUG] Audio RMS: {rms}")
            return rms < self.silent_threshold
        except Exception as e:
            print(f"[ERROR] Failed to check silence: {e}")
            return True  # Treat as silent if there's an error
    
    def record_and_save(self, save_dir):
        """Record audio and save it to a file in the specified directory."""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        audio_data = self.record_audio()
        file_name = f"recording_{int(time.time())}.wav"
        file_path = os.path.join(save_dir, file_name)
        self.save_audio(audio_data, file_path)
        return file_path

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
