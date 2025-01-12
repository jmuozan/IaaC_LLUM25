from pythonosc import dispatcher, osc_server
import asyncio

# Queue to communicate with the main flow
osc_queue = None

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

async def start_osc_receiver(queue, host="0.0.0.0", port=8009):
    """
    Start the OSC receiver on the specified host and port.
    """
    global osc_queue
    osc_queue = queue

    # Configure the dispatcher for handling OSC messages
    disp = dispatcher.Dispatcher()
    disp.map("/hello", osc_message_handler)

    # Run the OSC server
    loop = asyncio.get_event_loop()
    server = osc_server.AsyncIOOSCUDPServer((host, port), disp, loop)
    transport, protocol = await server.create_serve_endpoint()

    print(f"[OSC RECEIVER] Listening for OSC messages on {host}:{port}")
    return transport, protocol
