from pythonosc import dispatcher, osc_server
from pythonosc import udp_client
import asyncio

# Add OSC client for sending messages
osc_client = None
osc_queue = None

def setup_osc_client(client_host="192.168.0.130", client_port=8009):
    """Setup OSC client for sending messages back"""
    global osc_client
    print(f"Setting up OSC client to send to {client_host}:{client_port}")
    osc_client = udp_client.SimpleUDPClient(client_host, client_port)
    return osc_client

def send_osc_message(address, value):
    """Send OSC message using the client"""
    if osc_client:
        try:
            osc_client.send_message(address, value)
            print(f"[OSC SENDER] Successfully sent message to {address}: {value}")
        except Exception as e:
            print(f"[OSC SENDER] Error sending message: {e}")
    else:
        print("[OSC SENDER] Client not initialized")

def osc_message_handler(address, *args):
    """
    Handle incoming OSC messages and push them to the queue.
    """
    global osc_queue
    if osc_queue:
        print(f"[OSC RECEIVER] Received message at {address}: {args}")
        if address == "/hello":
            if args and args[0] == "record":
                asyncio.run_coroutine_threadsafe(osc_queue.put("record"), asyncio.get_event_loop())
            elif args and args[0] == "pause":
                asyncio.run_coroutine_threadsafe(osc_queue.put("pause"), asyncio.get_event_loop())

async def start_osc_receiver(queue, host="0.0.0.0", port=8009, client_port=8009):
    """
    Start the OSC receiver on the specified host and port.
    """
    global osc_queue
    osc_queue = queue

    # Setup OSC client for sending messages
    setup_osc_client(client_port=client_port)

    # Configure the dispatcher for handling OSC messages
    disp = dispatcher.Dispatcher()
    disp.map("/hello", osc_message_handler)

    # Run the OSC server
    loop = asyncio.get_event_loop()
    server = osc_server.AsyncIOOSCUDPServer((host, port), disp, loop)
    transport, protocol = await server.create_serve_endpoint()

    print(f"[OSC RECEIVER] Listening for OSC messages on {host}:{port}")
    return transport, protocol

def handle_osc_message(unused_addr, args, state):
    print(f"[OSC] Received message: {state}")
    if state == "record":
        print("[OSC] Sending generating state")
        send_osc_message("/state", "generating")
    elif state == "pause":
        print("[OSC] Sending pause state")
        send_osc_message("/state", "pause")
    elif state == "transcribing":
        print("[OSC] Sending transcribing state")
        send_osc_message("/state", "transcribing")
    elif state == "ready":
        print("[OSC] Sending ready state")
        send_osc_message("/state", "ready")

if __name__ == "__main__":
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/hello", handle_osc_message, "state")

    ip = "0.0.0.0"  # Listen on all available interfaces
    port = 8009

    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
    print(f"Serving on {server.server_address}")

    server.serve_forever()