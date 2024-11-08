from Speech2Text_V3 import SpeechToText

# Initialize SpeechToText instance with your API key
stt = SpeechToText(api_key="your_openai_api_key")  # Replace with your actual API key

def handle_trigger_signal(signal):
    """Function to handle incoming signals and trigger transcription if signal is (1,)"""
    if signal == (1,):  # Check if the signal matches (1,)
        stt.record_and_transcribe()

# Example usage: Simulate receiving the (1,) signal
if __name__ == "__main__":
    received_signal = (1,)  # Replace this with actual signal receiving logic
    handle_trigger_signal(received_signal)


