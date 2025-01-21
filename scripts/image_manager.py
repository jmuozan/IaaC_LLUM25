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

app = FastAPI()

# Paths
IMAGE_UPDATE_URL = "http://127.0.0.1:8001/update-image"
WEB_UPDATE_IMAGE_URL = "http://127.0.0.1:8001/update-image"


@app.post("/generate-image")
async def generate_image_endpoint(request: Request):
    """
    Endpoint to generate an image based on a prompt.
    """
      # Read the prompt from the request payload
    data = await request.json()
    combined_prompt = data.get("prompt")
    question = data.get("question")  # Get the question separately

    if not combined_prompt:
        return JSONResponse(content={"error": "Prompt is required"}, status_code=400)

    print(f"[INFO] Generating image with prompt: {combined_prompt}")

    try:
        # Define the system role for the image generation
        system_role = (
            "You are an AI model specializing in collaborative art generation for an outdoor light exhibition in Poblenou, Barcelona."
            #"Use One line drawing ideas"
            "Use comic style drawings"
            "always use black background"
            #"Your role is to merge multiple user inputs that answer a question into an artistic handdrawing using neon colors."
            #"Draw Realistic and relatable contents, that are easy to understand."
            #"Use thick outlines and strong neon colors on a consistent black background."
            "Avoid photorealism; ensure the style is abstract, bold, and highly contrasting."
            "Avoid violence, brutal or sexual outputs."
        )

        # Model the final prompt
        final_prompt = (
            f"{system_role}\n\n"
            f"Here is the Question: {question}\n"
            f"Here is the collaborative answer: {combined_prompt}.\n"
            "Create a single, cohesive artwork based on these answers."
        )
        print(final_prompt)
        # Generate image with the modeled prompt
        image_path = generate_image(final_prompt)
        # Call your image generation logic
        img_filename = generate_image(final_prompt)  # Assume this returns just the filename
        image_path = f"/{img_filename}"  # Construct relative path
        image_path = image_path.replace("\\", "/")  # Normalize path for the web


        return {"status": "success", "image_path": image_path}
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)

