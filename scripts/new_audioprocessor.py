import os
import soundfile as sf
import sounddevice as sd
import numpy as np
import time
import webrtcvad
import struct

class NewAudioProcessor:
    def __init__(self, rate=44100, channels=1, record_seconds=5, silence_threshold=0.01, vad_mode=2):
        self.rate = rate
        self.channels = channels
        self.record_seconds = record_seconds
        self.silence_threshold = silence_threshold  # RMS threshold
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(vad_mode)  # 0 (most permissive) to 3 (most strict)

    def record_audio(self):
        """Record audio for a fixed duration."""
        print("[DEBUG] Recording audio...")
        audio_data = sd.rec(int(self.record_seconds * self.rate), samplerate=self.rate, channels=self.channels)
        sd.wait()
        print("[DEBUG] Recording complete.")
        return audio_data

    def is_silent(self, audio_data):
        """Check if the audio is silent based on RMS (Root Mean Square) energy."""
        rms = np.sqrt(np.mean(audio_data**2))  # Calculate RMS energy
        print(f"[DEBUG] Audio RMS: {rms}")
        return rms < self.silence_threshold

    def is_speech(self, audio_data):
        """Check if the recorded audio contains speech."""
        try:
            # Convert to 16-bit PCM
            raw_data = (audio_data * 32767).astype(np.int16)  # Convert to 16-bit PCM
            frame_duration_ms = 10  # Use 10ms frames
            frame_length = int(self.rate * frame_duration_ms / 1000)  # Samples per frame

            # Split audio into chunks of frame_length
            frames = [raw_data[i:i + frame_length] for i in range(0, len(raw_data), frame_length)]
            if len(frames) == 0:
                print("[DEBUG] No valid frames for VAD processing.")
                return False

            # Check each frame with VAD
            for frame in frames:
                if len(frame) < frame_length:
                    print("[DEBUG] Frame too short for VAD. Skipping.")
                    continue
                if self.vad.is_speech(frame.tobytes(), self.rate):
                    print("[DEBUG] Speech detected in frame.")
                    return True

            print("[DEBUG] No speech detected in any frame.")
            return False
        except Exception as e:
            print(f"[ERROR] VAD processing error: {e}")
            return False



    def save_audio(self, audio_data, filename):
        """Save recorded audio to a file."""
        sf.write(filename, audio_data, self.rate)
        print(f"[DEBUG] Audio saved as {filename}")
        return filename

    def record_and_save(self, save_dir):
        """Record audio, check for speech, and save it to a file if it contains speech."""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        audio_data = self.record_audio()

        # Check RMS before VAD
        rms = np.sqrt(np.mean(audio_data**2))
        print(f"[DEBUG] Audio RMS: {rms}")
        if rms < 0.01:
            print("[INFO] Audio is silent or too quiet. Ignoring this recording.")
            return None

        # Check for speech using VAD
        if not self.is_speech(audio_data):
            print("[INFO] No speech detected. Ignoring this recording.")
            return None

        # Save valid audio
        file_name = f"recording_{int(time.time())}.wav"
        file_path = os.path.join(save_dir, file_name)
        self.save_audio(audio_data, file_path)
        print(f"[DEBUG] Saved audio file: {file_path}")
        return file_path

