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
    timestamp = int(time.time())
    filename = f"generated_image_{timestamp}.jpeg"
    
    # Create absolute path using normpath to handle slashes correctly
    full_path = os.path.normpath(os.path.join(os.path.dirname(__file__), IMAGE_FOLDER, filename))
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    response = client.images.generate(model="dall-e-3", prompt=final_prompt, n=1, size="1024x1024")
    image_url = response.data[0].url
    
    # Download and save image immediately
    try:
        img_data = requests.get(image_url).content
        with open(full_path, 'wb') as f:
            f.write(img_data)
        print(f"[DEBUG] Image saved to: {full_path}")
        
        # Verify file exists
        if not os.path.exists(full_path):
            raise Exception(f"File not saved at {full_path}")
            
    except Exception as e:
        print(f"[ERROR] Failed to save image: {e}")
        raise e
    
    return {
        "filename": full_path,
        "web_path": f"/static/Generated_Images/{filename}",
        "image_url": image_url
    }

async def save_image(url, filepath):
    """Asynchronous function to save the image"""
    img_data = requests.get(url).content
    with open(filepath, "wb") as handler:
        handler.write(img_data)
    return filepath

# size="1792x1024"  # Landscape format