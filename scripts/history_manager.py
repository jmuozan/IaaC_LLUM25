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
    Clear existing sentences and add new ones with "in-progress" status.
    Returns the updated list of sentences.
    """
    try:
        # Create new sentences list
        sentences = []
        for sentence_text in new_sentences:
            sentences.append({"text": sentence_text, "status": "in-progress"})

        # Save new sentences (overwrites existing file)
        with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
            json.dump(sentences, file, indent=4)

        return sentences
    except Exception as e:
        print(f"[ERROR] Failed to add new 'in-progress' sentences: {e}")
        return []

def finalize_sentences():
    """
    Mark all current sentences as "done".
    Returns the updated list of sentences.
    """
    try:
        if not os.path.exists(SENTENCES_FILE):
            print("[INFO] No existing sentences to finalize.")
            return []

        with open(SENTENCES_FILE, "r", encoding="utf-8") as file:
            sentences = json.load(file)

        # Mark all sentences as done
        for sentence in sentences:
            sentence["status"] = "done"

        # Save the updated list
        with open(SENTENCES_FILE, "w", encoding="utf-8") as file:
            json.dump(sentences, file, indent=4)

        return sentences
    except Exception as e:
        print(f"[ERROR] Failed to finalize sentences: {e}")
        return []