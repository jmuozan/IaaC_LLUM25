import paho.mqtt.client as mqtt
import time
import json

class ESP32MQTTClient:
    def __init__(self, broker="localhost", port=1883, client_id="python_client"):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id)
        
        # Set up callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Topics
        self.topic_prefix = "esp32/"
        self.subscribe_topics = [
            self.topic_prefix + "status",
            self.topic_prefix + "sensor_data"
        ]

    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            print("Connected to MQTT broker successfully")
            # Subscribe to all topics
            for topic in self.subscribe_topics:
                client.subscribe(topic)
                print(f"Subscribed to {topic}")
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        """Callback for when a message is received."""
        try:
            payload = json.loads(msg.payload.decode())
            print(f"Received message on topic {msg.topic}:")
            print(json.dumps(payload, indent=2))
        except json.JSONDecodeError:
            print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

    def connect(self):
        """Connect to the MQTT broker."""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Connection error: {e}")

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()

    def publish_message(self, subtopic, message):
        """Publish a message to a specific subtopic."""
        full_topic = self.topic_prefix + subtopic
        if isinstance(message, (dict, list)):
            message = json.dumps(message)
        self.client.publish(full_topic, message)
        print(f"Published to {full_topic}: {message}")

# Example usage
if __name__ == "__main__":
    # Create MQTT client
    mqtt_client = ESP32MQTTClient(
        broker="localhost",  # Change to your MQTT broker address
        port=1883,          # Change if using a different port
        client_id="python_computer"
    )
    
    # Connect to broker
    mqtt_client.connect()
    
    try:
        # Example: Publish a command to the ESP32
        while True:
            # Publish sample data
            mqtt_client.publish_message("command", {
                "action": "led_control",
                "state": "toggle"
            })
            time.sleep(5)  # Wait 5 seconds between messages
            
    except KeyboardInterrupt:
        print("\nDisconnecting from broker...")
        mqtt_client.disconnect()