#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleStatus, VehicleLocalPosition

class OffboardTrajectories(Node):
    def __init__(self):
        super().__init__('offboard_trajectories_node')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.offboard_control_mode_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.trajectory_setpoint_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile)
        self.vehicle_command_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos_profile)
    
        self.status_sub = self.create_subscription(VehicleStatus, '/fmu/out/vehicle_status_v1', self.status_callback, qos_profile)
        self.pos_sub = self.create_subscription(VehicleLocalPosition, '/fmu/out/vehicle_local_position_v1', self.pos_callback, qos_profile)

        #CHANGE ALTITUDE HERE
        self.target_alt = -5.0 
        self.current_pos = [0.0, 0.0, 0.0]
        self.nav_state = 0
        self.waypoint_index = 0
        
        # CHANGE SHAPE HERE
        self.active_shape = 'square' 
        self.waypoints = self.generate_path(self.active_shape)

        self.timer = self.create_timer(0.1, self.timer_callback)

    def generate_path(self, shape):
        s = 5.0 
        if shape == 'square':
            return [[0,0,self.target_alt], [s,0,self.target_alt], [s,s,self.target_alt], [0,s,self.target_alt], [0,0,self.target_alt]]
        elif shape == 'triangle':
            return [[0,0,self.target_alt], [s,0,self.target_alt], [s/2, s*0.866, self.target_alt], [0,0,self.target_alt]]
        elif shape == 'figure8':
            return [[3*np.sin(t), 3*np.sin(t)*np.cos(t), self.target_alt] for t in np.linspace(0, 2*np.pi, 30)]

    def pos_callback(self, msg):
        self.current_pos = [msg.x, msg.y, msg.z]

    def status_callback(self, msg):
        self.nav_state = msg.nav_state

    def timer_callback(self):
        self.publish_offboard_control_mode()

        if self.nav_state != VehicleStatus.NAVIGATION_STATE_OFFBOARD:
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
        else:
            target = self.waypoints[self.waypoint_index]
            self.publish_trajectory_setpoint(target[0], target[1], target[2])

            dist = np.linalg.norm(np.array(self.current_pos[:2]) - np.array(target[:2]))
            if dist < 0.4:
                if self.waypoint_index < len(self.waypoints) - 1:
                    self.waypoint_index += 1
                    self.get_logger().info(f"Moving to Waypoint {self.waypoint_index}")
                else:
                    self.get_logger().info("Mission Complete. Landing.")
                    self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)

    def publish_offboard_control_mode(self):
        msg = OffboardControlMode()
        msg.position, msg.velocity, msg.acceleration = True, False, False
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_control_mode_pub.publish(msg)

    def publish_trajectory_setpoint(self, x, y, z):
        msg = TrajectorySetpoint()
        msg.position = [x, y, z]
        msg.yaw = 1.5707
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.trajectory_setpoint_pub.publish(msg)

    def publish_vehicle_command(self, command, p1=0.0, p2=0.0):
        msg = VehicleCommand(command=command, param1=p1, param2=p2, target_system=1, target_component=1, source_system=1, source_component=1, from_external=True)
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = OffboardTrajectories()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
