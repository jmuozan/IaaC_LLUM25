from openai import OpenAI
import os
import requests
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMAGE_FOLDER = os.path.join("static", "Generated_Images")
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def generate_image(prompt):
    response = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    img_filename = os.path.join(IMAGE_FOLDER, "generated_image.jpeg")
    with open(img_filename, "wb") as handler:
        handler.write(img_data)
    return img_filename
