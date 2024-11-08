from pythonosc import dispatcher
from pythonosc import osc_server
import argparse

def message_handler(address, *args):
    """Callback function to handle incoming OSC messages"""
    print(f"Received message {address}: {args}")

def setup_osc_receiver(ip="10.43.0.101", port=9999):
    """Setup and start the OSC server"""
    # Create dispatcher
    disp = dispatcher.Dispatcher()
    # Register the message handler for all addresses
    disp.set_default_handler(message_handler)
    
    # Create and start server
    server = osc_server.ThreadingOSCUDPServer(
        (ip, port),
        disp
    )
    print(f"Serving on {server.server_address}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    # Command line arguments for IP and port
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="10.43.0.101",
        help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9999,
        help="The port to listen on")
    args = parser.parse_args()
    
    setup_osc_receiver(args.ip, args.port)