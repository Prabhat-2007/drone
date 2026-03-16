# drone


Scout Drone:
Flight Controller-	Cube Orange+:
ESC-	T-Motor Alpha 60A FOC (IP55)
Motors-	T-Motor MN601-S
Battery- Semi-Solid State 6S 30Ah
Precision GPS- 	Here4 RTK
onboard processing- NVIDIA Jetson Orin Nano
camera- DJI Zenmuse H30T

delivery drone:
Flight Controller-	Pixhawk 6X (High Compute)
ESC-		Hobbywing XRotor Pro 80A (HV)
Motors-		T-Motor U15 II (Raw Lift)
Battery-	Semi-Solid State 12S 44Ah
Onboard processing-	N/A (GPS Guided)
Precision GPS-Here4 RTK (cm-level)

Scout Drone
Autonomous grid-based mapping of the 30-hectare area.
High-efficiency quadcopter (e.g., T-Motor MN601-S) with a NVIDIA Jetson Orin nano.
Runs a YOLOv11 object detection model for real-time human identification. Sends a live 1080p/4K video feed and MAVLink metadata back to the Ground Station.

Ground Station 
QGroundControl for flight monitoring and a custom ROS2 middleware.
When the Scout detects a human, the GCS calculates the survivor's coordinates using the drone's position, altitude, and camera angle.
Once the operator confirms a detection, the GCS creates a new mission waypoint and pushes it directly to the Delivery Drone.

Delivery Drone
Precision delivery of medical kits, food, or other items.
Heavy-lift hexacopter with an automated winch system.
Waits in a "Standby" state at the base. Upon receiving coordinates, it launches autonomously, flies to the survivor, and lowers the payload without needing to land in hazardous floodwater.


CIRKIT DIAGRAM
*cameras, sensors, etc yet to be placed
https://app.cirkitdesigner.com/project/99ebaadb-3ad3-4114-80ba-c541705d3886
