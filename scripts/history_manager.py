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


def add_sentences_in_progress(new_sentences):
    """
    Add new sentences to `sentences.json` with the status "in-progress".
    Returns the updated list of sentences.
    """
    try:
        # Load existing sentences
        sentences = []
        if os.path.exists(SENTENCES_FILE):
            with open(SENTENCES_FILE, "r", encoding="utf-8") as file:
                sentences = json.load(file)

        # Add new sentences if not already present
        for sentence_text in new_sentences:
            if not any(s["text"] == sentence_text for s in sentences):
                sentences.append({"text": sentence_text, "status": "in-progress"})

        # Save updated sentences
        with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
            json.dump(sentences, file, indent=4)

        # print(f"[INFO] Added new 'in-progress' sentences: {new_sentences}")
        return sentences
    except Exception as e:
        print(f"[ERROR] Failed to add new 'in-progress' sentences: {e}")
        return []

def finalize_sentences():
    """
    Mark the first three "in-progress" sentences as "done",
    remove older "done" sentences, and keep the latest three.
    Returns the updated list of sentences.
    """
    try:
        # Load existing sentences
        if not os.path.exists(SENTENCES_FILE):
            print("[INFO] No existing sentences to finalize.")
            return []

        with open(SENTENCES_FILE, "r", encoding="utf-8") as file:
            sentences = json.load(file)

        # Separate "in-progress" and "done"
        in_progress = [s for s in sentences if s["status"] == "in-progress"]
        done = [s for s in sentences if s["status"] == "done"]

        # Mark the first three "in-progress" as "done"
        for sentence in in_progress[:3]:
            sentence["status"] = "done"

        # Combine updated "done" sentences and trim older ones
        done = done + in_progress[:3]
        done = done[-3:]  # Keep only the newest three "done"

        # Update "in-progress" sentences
        in_progress = in_progress[3:]  # Remove the processed ones

        # Save the updated list
        updated_sentences = in_progress + done
        with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
            json.dump(updated_sentences, file, indent=4)

        # print("[INFO] Finalized sentences. Updated JSON:")
        # print(json.dumps(updated_sentences, indent=4))
        return updated_sentences
    except Exception as e:
        print(f"[ERROR] Failed to finalize sentences: {e}")
        return []