from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/start-transcription")
async def start_transcription(request: Request):
    """
    Endpoint to handle transcription start requests from ESP32.
    """
    try:
        data = await request.json()
        print(f"[INFO] Received data: {data}")
        # You can add additional logic here, such as triggering transcription
        return JSONResponse(content={"status": "success", "message": "Transcription started."})
    except Exception as e:
        print(f"[ERROR] Failed to process request: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)