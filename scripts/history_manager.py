import os
from collections import deque

HISTORY_FILE = "history.txt"
MAX_HISTORY_LINES = 6

def update_and_get_history(new_inputs):
    history = deque(maxlen=MAX_HISTORY_LINES)
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as file:
            for line in file:
                history.append(line.strip())

    history.extend(new_inputs)
    with open(HISTORY_FILE, "a") as file:
        for input in new_inputs:
            file.write(f"{input}\n")

    return list(history)
