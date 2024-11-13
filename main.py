import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import wave
import pyaudio
import time
from collections import deque

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Folder to store generated images
IMAGE_FOLDER = "Generated_Images"
HISTORY_FILE = "history.txt"
MAX_HISTORY_LINES = 6

# Ensure the image folder exists
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

class AudioProcessor:
    def __init__(self, record_seconds=5, rate=44100, channels=1):
        self.client = client
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = channels
        self.rate = rate
        self.record_seconds = record_seconds
        self.audio = pyaudio.PyAudio()
        
    def record_audio(self):
        """Record audio and return the frames."""
        print(f"Recording for {self.record_seconds} seconds...")
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        
        for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
            if i % int(self.rate / (self.chunk * 2)) == 0:
                seconds_left = self.record_seconds - (i * self.chunk / self.rate)
                print(f"Recording... {seconds_left:.1f} seconds left", end='\r')
        
        print("\nFinished!")
        
        stream.stop_stream()
        stream.close()
        
        return frames
    
    def save_audio(self, frames, filename="temp.wav"):
        """Save recorded audio to WAV file."""
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio file using Whisper."""
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

class ImageGenerator:
    def __init__(self, system_role):
        self.system_role = system_role

    def get_next_image_filename(self):
        """Find the next available filename in the IMAGE_FOLDER."""
        existing_files = os.listdir(IMAGE_FOLDER)
        image_numbers = [
            int(f.split("_")[1].split(".")[0]) for f in existing_files if f.startswith("image_") and f.endswith(".jpeg")
        ]
        next_number = max(image_numbers) + 1 if image_numbers else 1
        return f"image_{next_number}.jpeg"
    
    def update_and_get_history(self, new_inputs):
        """Update and retrieve history."""
        history = deque(maxlen=MAX_HISTORY_LINES)
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as file:
                for line in file:
                    history.append(line.strip())
        
        history.extend(new_inputs)
        with open(HISTORY_FILE, "a") as file:
            for input in new_inputs:
                file.write(f"{input}\n")
        
        return list(history)
    
    def generate_image(self, user_inputs):
        """Generate image based on combined prompt."""
        history_inputs = self.update_and_get_history(user_inputs)
        combined_history = ". ".join(history_inputs)
        combined_inputs = ". ".join(user_inputs)
        final_prompt = (
            f"{self.system_role}\n\n"
            f"Here is the collaborative context from multiple users: {combined_inputs}. "
            f"Additionally, here is the recent history of inputs: {combined_history}. "
        )

        try:
            response = client.images.generate(model="dall-e-3", prompt=final_prompt, n=1, size="1024x1024")
            image_url = response.data[0].url
            print(f"Image URL: {image_url}")

            img_data = requests.get(image_url).content
            img_filename = self.get_next_image_filename()
            img_filepath = os.path.join(IMAGE_FOLDER, img_filename)

            with open(img_filepath, 'wb') as handler:
                handler.write(img_data)

            print(f"Image saved as {img_filepath}")
            return img_filepath
        except Exception as e:
            print(f"Error generating image: {e}")
            return None

def main():
    # Define the system role
    system_role = (
        "You are an AI model specializing in collaborative art generation. "
        "Combine multiple user inputs in a hand-drawn, child-like sketch style with a focus on neon colors on a black background."
    )
    audio_processor = AudioProcessor()
    image_generator = ImageGenerator(system_role)
    user_inputs = []

    # Collect 3 inputs
    for i in range(1, 4):
        frames = audio_processor.record_audio()
        audio_processor.save_audio(frames, f"temp_recording_{i}.wav")
        transcription = audio_processor.transcribe_audio(f"temp_recording_{i}.wav")
        
        if transcription:
            print(f"Person {i}'s input: {transcription}")
            user_inputs.append(transcription)

    # Generate the image
    img_path = image_generator.generate_image(user_inputs)
    print("Process complete.")

if __name__ == "__main__":
    main()


