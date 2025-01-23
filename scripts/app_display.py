import json
import os
import asyncio
from fastapi import FastAPI, WebSocket, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from typing import List
import uvicorn

# Initialize app
app = FastAPI()

# Path setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SENTENCES_FILE = os.path.join(BASE_DIR, "sentences.json")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
# Global variable to store the current question
current_question = "Default question"
# WebSocket clients
clients = set()  # Set to keep track of WebSocket connections
# Helper Functions
def load_sentences():
    """Load sentences from JSON file."""
    try:
        with open(SENTENCES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_sentences(sentences: List[dict]):
    """Save sentences to JSON file."""
    with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
        json.dump(sentences, file, indent=4)

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main HTML page."""
    sentences = load_sentences()
    return templates.TemplateResponse(
        "index.html", {"request": request, "sentences": sentences}
    )

@app.post("/update-sentences")
async def update_sentences(request: Request):
    data = await request.json()
    with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    await notify_clients("update_sentences", data)
    return {"status": "success"}

@app.post("/state-update")
async def state_update(request: Request):
    """Notify WebSocket clients of recording and transcribing states."""
    data = await request.json()
    state = data.get("state")
    if state:
        await notify_clients("state_update", {"state": state})
        print(f"[INFO] State updated to: {state}")
        return {"status": "success"}
    return {"error": "Invalid state"}, 400

@app.post("/update-counter")
async def update_counter(request: Request):
    """Endpoint to update and broadcast the sentence counter."""
    data = await request.json()
    count = data.get("count")
    if count is not None:
        await notify_clients("update_counter", {"count": count})
        return {"status": "success"}
    return {"error": "Invalid count"}, 400

@app.post("/update-image")
async def update_image(request: Request):
    data = await request.json()
    await notify_clients("update_image", data)
    return {"status": "success"}

@app.get("/current-question")
async def get_current_question():
    """Endpoint to fetch the current question."""
    global current_question
    print(f"[DEBUG] Returning current_question: {current_question}")
    return {"current_question": current_question}
    
@app.post("/update-question")
async def update_question(request: Request):
    """Endpoint to update the current question."""
    global current_question
    data = await request.json()
    print(f"[DEBUG] Received data for update-question: {data}")
    current_question = data.get("question", "How will living in cities look like in the future ?")
    print(f"[DEBUG] Updated current_question to: {current_question}")
    await notify_clients("current_question", {"question": current_question})
    return {"status": "success", "current_question": current_question}


# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global current_question
    await websocket.accept()
    clients.add(websocket)  # Add the client to the set
    print(f"[INFO] WebSocket connection opened. Total clients: {len(clients)}")

    try:
        # Send existing sentences on connection
        sentences = load_sentences()
        await websocket.send_json({"event": "init_sentences", "data": sentences})
        await websocket.send_json({"event": "current_question", "data": current_question})
        # print("[DEBUG] Sent existing sentences to new client.")

        # Keep listening for messages (if needed in the future)
        while True:
            try:
                data = await websocket.receive_json()
                # print("[DEBUG] WebSocket message received:", data)

                event = data.get("event")
                if event == "update_question":
                    new_question = data.get("data")
                    if new_question:
                        current_question = new_question
                        print(f"[INFO] Updated current question: {current_question}")
                        await notify_clients("current_question", {"data": current_question})
                elif event == "get_current_question":
                    await websocket.send_json({"event": "current_question", "data": current_question})
            
            except asyncio.CancelledError:
                print("[INFO] WebSocket operation cancelled.")
                break

            except Exception as e:
                print(f"[ERROR] Failed to process WebSocket message: {e}")
                break
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
    finally:
        clients.remove(websocket)  # Remove the client on disconnect
        print(f"[INFO] WebSocket connection closed. Total clients: {len(clients)}")

async def notify_clients(event, data):
    message = {"event": event, "data": data}
    for client in clients:
        await client.send_json(message)

# Exception Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[ERROR] Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"message": "Internal server error."})


# Run the app
if __name__ == "__main__":
    uvicorn.run("app_display:app", host="127.0.0.1", port=8001, reload=True, timeout_keep_alive=300)
