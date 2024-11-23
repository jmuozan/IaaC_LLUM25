def update_and_get_history(transcriptions, max_lines=10, history_file = "history.txt"):

    # Ensure the file exists
    with open(history_file, "a", encoding="utf-8") as file:
        pass

    # Write new transcriptions to the file
    with open(history_file, "a", encoding="utf-8") as file:
        for input in transcriptions:
            file.write(f"{input}\n")

    # Read history and keep only the last `max_lines` entries
    with open(history_file, "r", encoding="utf-8") as file:
        history = file.readlines()

    history = history[-max_lines:]  # Keep only the last `max_lines` entries

    # Write the trimmed history back to the file
    with open(history_file, "w", encoding="utf-8") as file:
        file.writelines(history)

    # Return the trimmed history as a list of stripped lines
    return [line.strip() for line in history]

