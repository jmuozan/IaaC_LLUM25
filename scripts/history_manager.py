import json
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SENTENCES_FILE = os.path.join(BASE_DIR, "sentences.json")

def append_to_history(transcriptions, history_file="history.txt", max_lines=6):
    """Append new transcriptions to `history.txt` and trim to `max_lines`."""
    try:
        with open(history_file, "a", encoding="utf-8") as file:
            for transcription in transcriptions:
                file.write(f"{transcription}\n")
        
        # Trim history to the last `max_lines`
        with open(history_file, "r", encoding="utf-8") as file:
            lines = file.readlines()[-max_lines:]
        
        with open(history_file, "w", encoding="utf-8") as file:
            file.writelines(lines)
    except Exception as e:
        print(f"[ERROR] Failed to append to history: {e}")

def update_sentences_json(history_file="history.txt", json_file=SENTENCES_FILE, max_sentences=6):
    """
    Sync `sentences.json` with the latest state of `history.txt`.

    Updates statuses:
    - "in-progress": Sentences being used for the current image generation.
    - "done": Sentences from previous image generations.
    Keeps a maximum of `max_sentences` entries (3 in-progress, 3 done).
    """
    try:
        # Read the current state of `history.txt`
        with open(history_file, "r", encoding="utf-8") as file:
            history = [line.strip() for line in file.readlines()]

        # Trim to the last `max_sentences`
        history = history[-max_sentences:]

        # Read or initialize the current sentences state
        sentences = []
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as json_f:
                try:
                    sentences = json.load(json_f)
                except json.JSONDecodeError:
                    pass

        # Update statuses
        updated_sentences = []
        for idx, line in enumerate(history):
            status = "in-progress" if idx < 3 else "done"
            updated_sentences.append({"text": line, "status": status})

        # Write the updated list to `sentences.json`
        with open(json_file, "w", encoding="utf-8") as json_f:
            json.dump(updated_sentences, json_f, indent=4)

        print(f"[INFO] Updated sentences.json at {json_file}")
        return updated_sentences
    except Exception as e:
        print(f"[ERROR] Failed to update sentences.json: {e}")
        return []