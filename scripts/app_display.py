import json
from fastapi import FastAPI, Form, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from typing import List
import os
from time import time
import asyncio


# Paths and initialization
base_dir = os.path.abspath(os.path.dirname(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))
app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")

# Files and state
# static_dir = os.path.join(base_dir, "static")
SENTENCES_FILE = os.path.join(base_dir, "sentences.json")
websocket_clients = []
latest_image = None  # Store the latest image path

# Helper functions to load/save sentences
def load_sentences() -> List[str]:
    try:
        with open(SENTENCES_FILE, "r", encoding="utf-8") as file:
            sentences = json.load(file)
            print(f"[DEBUG] Loaded sentences: {sentences}")
            return sentences
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[DEBUG] Error loading sentences: {e}")
        save_sentences([])  # Create an empty file if it doesn't exist
        return []




def save_sentences(sentences: List[str]):
    with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
        json.dump(sentences, file)
    print(f"Sentences saved to {SENTENCES_FILE}: {sentences}")  # Debug log

#Notify HTML for new available packages
async def notify_clients(event=None, data=None):
    """Send event and data to all connected WebSocket clients."""
    message = {}
    if event:
        message["event"] = event
    if data:
        message["data"] = data
    else:
        # If no event/data provided, send grouped sentences
        sentences = load_sentences()
        grouped_sentences = [sentences[i:i + 3][::-1] for i in range(0, len(sentences), 3)][::-1]
        message["boxes"] = grouped_sentences

    for client in websocket_clients:
        try:
            await client.send_json(message)
        except Exception as e:
            print(f"[DEBUG] WebSocket error: {e}")
            websocket_clients.remove(client)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main page."""
    sentences = load_sentences()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "sentences": sentences, "image_path": latest_image}
    )

@app.post("/add-sentence")
async def add_sentence(sentence: str = Form(...)):
    """Receive a new sentence and notify clients."""
    sentences = load_sentences()
    sentences.append(sentence.strip())
    save_sentences(sentences[-12:])  # Save the updated list
    await notify_clients(event="new_sentence", data=sentence.strip())
    return {"status": "success", "message": "Sentence added."}

@app.post("/update-image")
async def update_image(request: Request):
    """Receive a new image path and notify clients."""
    data = await request.json()
    image_path = data.get("image_path")
    if not image_path:
        print("[DEBUG] No image path provided.")
        return {"status": "error", "message": "Image path is required."}
    print(f"[DEBUG] Received image update: {image_path}")
    # global latest_image
    # latest_image = image_path
    await notify_clients(event="update_image", data=image_path)
    return {"status": "success", "message": "Image updated."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)
    print("[DEBUG] WebSocket connection opened.")
    try:
        await notify_clients()
        while True:
            await asyncio.sleep(10)  # Keep the connection alive
    except Exception as e:
        print(f"[DEBUG] WebSocket error: {e}")
    finally:
        websocket_clients.remove(websocket)
        print("[DEBUG] WebSocket connection closed.")


import uvicorn

if __name__ == "__main__":
    uvicorn.run("app_display:app", host="127.0.0.1", port=8001, reload=True)
