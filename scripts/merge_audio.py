import soundfile as sf
import numpy as np

def merge_audio_files(audio_files, output_filename):
    """Merges multiple audio files into a single audio file.
    
    Args:
        audio_files (list): List of paths to audio files to merge.
        output_filename (str): The path to save the merged audio file.

    Returns:
        str: Path to the saved merged audio file.
    """
    if not audio_files:
        raise ValueError("No audio files provided for merging.")

    # Read and concatenate audio data
    combined_audio_data = []
    for file_path in audio_files:
        data, sample_rate = sf.read(file_path)
        combined_audio_data.append(data)
    
    # Concatenate all audio arrays
    combined_audio_data = np.concatenate(combined_audio_data)

