from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
import subprocess
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMAGE_FOLDER = os.path.join("static", "Generated_Images")
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def generate_image(final_prompt):
    timestamp = int(time.time())  # Unique timestamp for filenames
    filename = f"generated_image_{timestamp}.jpeg"

    response = client.images.generate(model="dall-e-3", prompt=final_prompt, n=1, size="1024x1024")
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    img_filename = os.path.join(IMAGE_FOLDER, filename)
    with open(img_filename, "wb") as handler:
        handler.write(img_data)
    return img_filename

