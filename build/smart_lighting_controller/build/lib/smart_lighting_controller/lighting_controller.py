import rclpy # Import ROS 2 Python library
from rclpy.node import Node # Import Node class for creating ROS 2 nodes
from std_msgs.msg import String # Import String message type for publishing light state
from datetime import datetime
import paho.mqtt.client as mqtt # Import MQTT client library for communicating with Zigbee2MQTT
import json


# Create a ROS 2 node that controls smart lights via MQTT based on a schedule
class LightingController(Node):
    """ROS 2 node for controlling smart lights via MQTT.

    Automatically turns lights ON at 8 PM and OFF at 8 AM.
    Publishes light state to ROS 2 and receives commands via MQTT.
    """

    def __init__(self):
        
        # Initialize the LightingController node
        super().__init__('lighting_controller')

        # Create a ROS 2 publisher 
        # It publishes String messages to the topic called 'light state'
        self.publisher_ = self.create_publisher(String, 'light_state', 10) # Queue size of 10 for outgoing messages

        # MQTT settings
        self.mqtt_broker = 'localhost' # MQTT broker address
        self.command_topic = 'zigbee2mqtt/0xa4c1380fccb9ffff/set' # Send ON/OFF command to the zigbee smart plug
        self.state_topic = 'zigbee2mqtt/0xa4c1380fccb9ffff' # Receive current state of zigbee smart plug

        # Prevents sending repeated commands within the same minute by storing the last minute command was sent
        self.last_command_time = None

        # MQTT client setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message

        try:
            # Connect to the MQTT broker at port 1883
            self.mqtt_client.connect(self.mqtt_broker, 1883, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            # If the connection fails, log the error and raise the exception to prevent the node from running without MQTT connectivity
            self.get_logger().error(f'Failed to connect to MQTT broker: {e}')
            raise

        # ROS 2 timer to check the schedule every 10 seconds
        self.timer = self.create_timer(10.0, self.check_schedule)
        self.get_logger().info('Smart lighting controller started.')

    # Handle MQTT connection callback
    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0: # Connection successful
            self.get_logger().info(f'Connected to MQTT broker with result code {rc}')
            client.subscribe(self.state_topic) # Subscribe to the topic to receive light state updates
        else:
            self.get_logger().error(f'Failed to connect to MQTT broker with result code {rc}')

    def on_mqtt_message(self, client, userdata, msg):
        payload = msg.payload.decode() # Decode the MQTT message payload from bytes to string
        
        try:
            data = json.loads(payload)
            light_state = data.get('state', payload)
        except json.JSONDecodeError:
            light_state = payload

        # Publish clean state string to ROS2
        ros_msg = String()
        ros_msg.data = light_state
        self.publisher_.publish(ros_msg)

        self.get_logger().info(f'Received light state from MQTT: {light_state}')
    
    # Send ON/OFF command to the smart plug via MQTT
    def send_light_command(self, command):
        payload = json.dumps({'state': command})
        self.mqtt_client.publish(self.command_topic, payload)
        self.get_logger().info(f'Sent MQTT command: {payload}')
    
    def check_schedule(self):
        now = datetime.now()
        current_time = now.strftime('%H:%M')

        # Skip if we already acted this minute
        if self.last_command_time == current_time:
            return

        # Turn ON at 8:00 PM
        if current_time == '20:00':
            self.send_light_command('ON')
            self.last_command_time = current_time
        # Turn OFF at 8:00 AM
        elif current_time == '08:00':
            self.send_light_command('OFF')
            self.last_command_time = current_time
    
# Main function of the program
def main(args=None):
    rclpy.init(args=args) # Initialize ROS 2
    node = LightingController()

    try:
        rclpy.spin(node) # Keep the ROS 2 node running
    except KeyboardInterrupt: # If user presses Ctrl+C, log the shutdown and exit gracefully
        pass
    finally:
        node.mqtt_client.loop_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

