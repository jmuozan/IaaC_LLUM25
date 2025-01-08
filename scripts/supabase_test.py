import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Define paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "static", "Generated_Images")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define bucket name
BUCKET_NAME = "created_images"

def upload_image_and_save_to_db(image_path, prompt):
    try:
       # Ensure the full path is used
        absolute_image_path = os.path.abspath(image_path)
        print(f"[INFO] Absolute image path: {absolute_image_path}")
        # Extract the file name (e.g., "generated_image.jpeg")
        file_name = os.path.basename(image_path)

        # Upload the image to the bucket
        with open(absolute_image_path, "rb") as file:
            upload_response = supabase.storage.from_(BUCKET_NAME).upload(file_name, file)
        print(f"[INFO] Upload response: {upload_response}")

        # Generate the public URL for the uploaded image
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
        print(f"[INFO] Image uploaded: {public_url}")

        # Save transcription and image URL to the database
        data = {"transcription": prompt, "image_url": public_url}
        save_response = supabase.table("transcriptions").insert(data).execute()
        print("[SUCCESS] Data saved to database:", save_response)
        
        print("[SUCCESS] Data saved to database.")
    except Exception as e:
        print(f"[ERROR] Failed to upload and save: {e}")
# Test script
# upload_image_and_save_to_db("scripts/static/Generated_Images/generated_image.jpeg", "This is a test transcription.")
