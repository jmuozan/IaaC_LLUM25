# Just for testing with myself.

from pythonosc import udp_client
import time

def create_sender():
    client = udp_client.SimpleUDPClient("127.0.0.1", 5005)
    
    try:
        while True:
            # Test message
            message = "Hello"
            client.send_message("/test", message)
            print(f"Sent message: {message}")
            
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStopping sender...")

if __name__ == "__main__":
    create_sender()