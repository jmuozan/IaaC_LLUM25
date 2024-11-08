from pythonosc import dispatcher
from pythonosc import osc_server
import threading

def handle_osc_message(address, *args):
    print(f"Received from {address}: {args}")

def start_osc_server(ip, port):
    # Create a dispatcher to handle incoming OSC messages
    disp = dispatcher.Dispatcher()
    disp.map("/LLUM", handle_osc_message)  # Map incoming messages on /LLUM

    # Create server
    server = osc_server.ThreadingOSCUDPServer((ip, port), disp)
    print(f"Serving on {server.server_address}")
    server.serve_forever()

if __name__ == "__main__":
    ip = "0.0.0.0"  # Listen on all available IPs
    port = 9999     # Port to listen on (should match outPort in Arduino code)

    # Start OSC server
    server_thread = threading.Thread(target=start_osc_server, args=(ip, port))
    server_thread.start()