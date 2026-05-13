# NTU Dorm Smart Lighting Automation

A ROS 2 (Jazzy) Python package that automates dorm room lighting to reduce electricity waste, turning lights **ON at 8:00 PM** and **OFF at 8:00 AM** via MQTT and Zigbee smart plug.

---

## Table of Contents
 
1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [Technologies Used](#3-technologies-used)
4. [Project Structure](#4-project-structure)
5. [Topics Reference](#5-topics-reference)
6. [Hardware Setup](#6-hardware-setup)
7. [Install Dependencies](#7-install-dependencies)
8. [Running the MQTT Broker](#8-running-the-mqtt-broker)
9. [Running Zigbee2MQTT](#9-running-zigbee2mqtt)
10. [Building the ROS 2 Package](#10-building-the-ros-2-package)
11. [Running the ROS 2 Node](#11-running-the-ros-2-node)
12. [Testing ON/OFF Commands](#12-testing-onoff-commands)
13. [Normal Run Procedure](#13-normal-run-procedure)
14. [Future Enhancements](#14-future-enhancement)

---

## 1. Overview

In student dormitories, lights are often left on overnight or during the day, wasting electricity. This project provides a scheduled lighting controller that addresses this by automatically turning lights on and off at fixed times.
 
**The ROS 2 node is responsible for:**
- Checking the current time periodically
- Sending ON/OFF commands to the smart plug via MQTT
- Receiving the current light state from MQTT
- Publishing the current light state to a ROS 2 topic

---

## 2. System Architecture

---

## 3. Technologies Used

| Category | Tool |
|---|---|
| OS | Ubuntu 24.04 |
| Robot framework | ROS 2 Jazzy |
| Language | Python 3 |
| Messaging | MQTT via Mosquitto |
| Python MQTT library | paho-mqtt |
| Zigbee bridge | Zigbee2MQTT (Docker) |
| Hardware | SONOFF Zigbee 3.0 USB Dongle Plus, SONOFF Zigbee Smart Plug Type G |

---

## 4. Project Structure

```text
ros2_ws/
└── src/
    └── smart_lighting_controller/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        │   └── smart_lighting_controller
        ├── smart_lighting_controller/
        │   ├── __init__.py
        │   └── lighting_controller.py
        └── README.md
```
---

## 5. Topics Reference

### MQTT Topics
| Purpose | Topic | Message |
|---|---|---|
| Send light command | `zigbee2mqtt/0xa4c1380fccb9ffff/set` | `{"state": "ON"}` / `{"state": "OFF"}` |
| Receive light state | `zigbee2mqtt/0xa4c1380fccb9ffff` | JSON state from Zigbee2MQTT |

### ROS 2 Topics
 
| Purpose | Topic | Message Type |
|---|---|---|
| Publish current light state | `/light_state` | `std_msgs/String` |
 
---

## 6. Hardware Setup

**Required hardware:**
- SONOFF Zigbee 3.0 USB Dongle Plus
- SONOFF Zigbee Smart Plug Type G
- A lamp or light connected to the smart plug

**Setup steps:**
 
1. Plug the SONOFF Zigbee USB Dongle into your laptop.
2. Plug the SONOFF Zigbee Smart Plug into a wall socket, then connect your lamp to the smart plug.
3. Find the dongle path (needed for Zigbee2MQTT configuration):
   ```bash
   ls /dev/serial/by-id/
   ```
4. In the Zigbee2MQTT dashboard, enable **Permit Join**, then hold the button on the smart plug for ~5 seconds until its light starts blinking. The plug will pair automatically.

---

## 7. Install Dependencies

```bash
# Update package list
sudo apt update
 
# Install Mosquitto MQTT broker and client tools
sudo apt install mosquitto mosquitto-clients
 
# Install Python MQTT library
sudo apt install python3-paho-mqtt
 
# Install colcon build tools
sudo apt install python3-colcon-common-extensions
 
# Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash
```
 
---

## 8. Running the MQTT Broker
 
Start Mosquitto:
```bash
sudo systemctl start mosquitto
```
 
Verify it is running:
```bash
sudo systemctl status mosquitto
```
 
Mosquitto runs as a system service in the background and will persist across terminals.
 
---

## 9. Running Zigbee2MQTT
 
Navigate to the Zigbee2MQTT folder and start it via Docker:
```bash
cd ~/zigbee2mqtt
sudo docker compose up -d
```
 
Open the Zigbee2MQTT dashboard in your browser:
```
http://localhost:8080
```
 
Zigbee2MQTT runs as a Docker container in the background.
 
---
 
## 10. Building the ROS 2 Package
 
```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```
 
> Rebuild and re-source whenever you modify the node's code.
 
---
 
## 11. Running the ROS 2 Node
 
Source ROS 2 and the workspace, then run the node:
```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run smart_lighting_controller lighting_controller
```
 
**Expected output:**
```
Smart lighting controller started.
Connected to MQTT broker with result code 0.
```
 
---
## 12. Testing ON/OFF Commands
 
Open three separate terminals to test the full communication chain.
 
### Terminal 1 — Subscribe to Zigbee2MQTT state topic
```bash
mosquitto_sub -h localhost -t zigbee2mqtt/0xa4c1380fccb9ffff
```
This shows raw state updates coming from the smart plug.
 
### Terminal 2 — Echo the ROS 2 light state topic
```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 topic echo /light_state
```
 
**Expected output:**
```
data: 'ON'
```
or
```
data: 'OFF'
```
 
### Terminal 3 — Send a manual MQTT command
 
Turn the light **ON**:
```bash
mosquitto_pub -h localhost -t zigbee2mqtt/0xa4c1380fccb9ffff/set -m '{"state": "ON"}'
```
 
Turn the light **OFF**:
```bash
mosquitto_pub -h localhost -t zigbee2mqtt/0xa4c1380fccb9ffff/set -m '{"state": "OFF"}'
```
 
You should see the state update appear in both Terminal 1 and Terminal 2.
 
---

## 13. Normal Run Procedure
 
A complete system requires three components running together:
 
**Step 1 — Start Mosquitto:**
```bash
sudo systemctl start mosquitto
```
 
**Step 2 — Start Zigbee2MQTT:**
```bash
cd ~/zigbee2mqtt
sudo docker compose up -d
```
 
**Step 3 — Run the ROS 2 node:**
```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run smart_lighting_controller lighting_controller
```
---

## 14. Future Enhancements

1. **Configuration File**: Move settings to YAML/JSON config
2. **Adjustable Schedules**: Use ROS 2 parameters or services to change times
3. **Manual Override**: Add ROS 2 service to manually control lights
4. **Sunrise/Sunset Integration**: Use calendar data instead of fixed times
5. **Sensor Integration**: React to presence sensors or light level
6. **Testing Suite**: Add unit tests and integration tests
7. **Docker Support**: Containerize for easier deployment

## License

MIT License - See LICENSE file for details

## Author

Eileen Teoh (eileenteoh10399@gmail.com)