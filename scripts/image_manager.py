import os
import json
import time
import requests
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
import sys
import os

# Add the parent directory to sys.path to locate the scripts folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.image_generator import generate_image
UPDATE_STATE_URL = "http://127.0.0.1:8001/state-update"
app = FastAPI()

# Paths
IMAGE_UPDATE_URL = "http://127.0.0.1:8001/update-image"
WEB_UPDATE_IMAGE_URL = "http://127.0.0.1:8001/update-image"
UPDATE_SENTENCES_URL = "http://127.0.0.1:8001/update-sentences"

async def update_state(state):
    """Send state update to the interface."""
    try:
        response = requests.post(UPDATE_STATE_URL, json={"state": state})
        response.raise_for_status()
        print(f"[INFO] State updated to: {state}")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to update state: {e}")

@app.post("/generate-image")
async def generate_image_endpoint(request: Request):
    """
    Endpoint to generate an image based on a prompt.
    """
    try:
        data = await request.json()
        combined_prompt = data.get("prompt")
        question = data.get("question")

        if not combined_prompt:
            return JSONResponse(content={"error": "Prompt is required"}, status_code=400)

        # Define the system role for the image generation
        system_role = (
            "You are an AI model specializing in collaborative art generation for an outdoor light exhibition in Poblenou, Barcelona. "
            "Always use a realistic cinematic architecture style with colors and focus on explaining details related to the inputs. "
            "Use high contrast and avoid complex scenes. "
            "Avoid sexual, brutal or harmfull contents. replace it with something beatiful instead "
        )

        # Model the final prompt
        final_prompt = (
            f"{system_role}\n\n"
            f"Question: {question}\n"
            f"Inputs: {combined_prompt}.\n"
        )
        print(final_prompt)
        # Generate image with the modeled prompt
        result = generate_image(final_prompt)
        print(f"[DEBUG] Generated image at: {result['filename']}")
        
        # Ensure URL has https:// prefix
        image_url = result['image_url']
        if not image_url.startswith(('http://', 'https://')):
            image_url = 'https://' + image_url
            print(f"[DEBUG] Fixed Image URL: {image_url}")
        
        # Return both the local path and the direct URL
        return {
            "status": "success", 
            "image_path": result['filename'],  # Return full path
            "direct_url": image_url
        }
        
    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        await update_state("image_generation_failed")
        
        # Clear the sentences on failure
        try:
            requests.post(UPDATE_SENTENCES_URL, json=[])
        except Exception as clear_err:
            print(f"[ERROR] Failed to clear sentences: {clear_err}")
            
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)

