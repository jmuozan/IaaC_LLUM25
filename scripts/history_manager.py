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
    Add new sentences with "in-progress" status, accumulating up to 3 items.
    Removes all "done" sentences when starting a new set.
    """
    try:
        # Load existing sentences
        if os.path.exists(SENTENCES_FILE):
            with open(SENTENCES_FILE, "r", encoding="utf-8") as file:
                sentences = json.load(file)
        else:
            sentences = []

        # Get current in-progress sentences
        in_progress = [s for s in sentences if s["status"] == "in-progress"]
        
        # If we already have 3 in-progress sentences, don't add more
        if len(in_progress) >= 3:
            print("[INFO] Already have 3 in-progress sentences. Skipping new additions.")
            return sentences

        # If this is the start of a new set (no current in-progress), remove all done sentences
        if len(in_progress) == 0:
            sentences = [s for s in sentences if s["status"] != "done"]

        # Add new sentences with "in-progress" status
        for sentence_text in new_sentences:
            if len(in_progress) < 3:  # Only add if we're under the limit
                new_sentence = {"text": sentence_text, "status": "in-progress"}
                sentences.append(new_sentence)
                in_progress.append(new_sentence)

        # Save updated sentences
        with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
            json.dump(sentences, file, indent=4)

        return sentences
    except Exception as e:
        print(f"[ERROR] Failed to add new 'in-progress' sentences: {e}")
        return []

def finalize_sentences():
    """
    Mark all current "in-progress" sentences as "done".
    """
    try:
        if not os.path.exists(SENTENCES_FILE):
            print("[INFO] No existing sentences to finalize.")
            return []

        with open(SENTENCES_FILE, "r", encoding="utf-8") as file:
            sentences = json.load(file)

        # Only mark in-progress sentences as done
        for sentence in sentences:
            if sentence["status"] == "in-progress":
                sentence["status"] = "done"

        # Save the updated list
        with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
            json.dump(sentences, file, indent=4)

        return sentences
    except Exception as e:
        print(f"[ERROR] Failed to finalize sentences: {e}")
        return []