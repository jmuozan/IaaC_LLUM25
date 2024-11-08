from pythonosc import dispatcher
from pythonosc import osc_server
import threading

# Function to handle OSC messages
def handle_osc_message(stt_callback, address, *args):
    print(f"{args}")
    if args and args[0] == 1:  # Check if the first argument is 1
        stt_callback()  # Call the provided callback function

# Function to start OSC server
def start_osc_server(ip, port, stt_callback):
    # Create a dispatcher to handle incoming OSC messages
    disp = dispatcher.Dispatcher()
    disp.map("/LLUM", handle_osc_message, stt_callback)  # Map messages on /LLUM to handler

    # Create server
    server = osc_server.ThreadingOSCUDPServer((ip, port), disp)
    print(f"Serving on {server.server_address}")
    server.serve_forever()

# Function to run the OSC server in a separate thread
def run_server(stt_callback, ip="0.0.0.0", port=9999):
    server_thread = threading.Thread(target=start_osc_server, args=(ip, port, stt_callback))
    server_thread.start()
