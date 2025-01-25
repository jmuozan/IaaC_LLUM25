import subprocess
import os
import time
import sys
import webbrowser

def check_openai_key():
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        print("⚠️ OpenAI API key not found!")
        key = input("Please enter your OpenAI API key: ")
        os.environ['OPENAI_API_KEY'] = key
    return True

def start_services():
    print("🚀 Starting LLUM25 services...")
    
    if not check_openai_key():
        return False

    try:
        # Update paths to use scripts directory
        scripts_dir = os.path.join(os.path.dirname(__file__))
        
        # Start FastAPI server (app_display.py)
        fastapi = subprocess.Popen([sys.executable, "app_display.py"], 
                                 cwd=scripts_dir)
        print("✅ FastAPI server started")
        time.sleep(2)  # Wait for server to start

        # Start Image Generation Service
        imagen = subprocess.Popen([sys.executable, "image_manager.py"],
                                cwd=scripts_dir)
        print("✅ Image generation service started")
        time.sleep(2)

        # Start main service (from parent directory)
        main = subprocess.Popen([sys.executable, "new_main.py"],
                              cwd=os.path.dirname(scripts_dir))
        print("✅ Main service started")
        time.sleep(2)

        # Open frontend in browser
        webbrowser.open('http://localhost:8001')
        print("✅ Frontend opened in browser")

        print("\n🎉 All services started!")
        print("\nPress Ctrl+C to stop all services")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            fastapi.terminate()
            imagen.terminate()
            main.terminate()
            print("✅ All services stopped")

    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return False

if __name__ == "__main__":
    start_services()