#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleStatus

class OffboardControl(Node):
    def __init__(self):
        super().__init__('offboard_takeoff_node')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.offboard_control_mode_pub = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.trajectory_setpoint_pub = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile)
        self.vehicle_command_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', qos_profile)

        self.status_sub = self.create_subscription(VehicleStatus, '/fmu/out/vehicle_status_v1', self.vehicle_status_callback, qos_profile)

        self.takeoff_height = -5.0  # CHANGE ALTITUDE HERE
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.nav_state = VehicleStatus.NAVIGATION_STATE_MAX
        self.dt = 0.1
        self.flight_time = 0.0

    def vehicle_status_callback(self, msg):
        self.nav_state = msg.nav_state

    def timer_callback(self):
        self.publish_offboard_control_mode()

        if self.nav_state != VehicleStatus.NAVIGATION_STATE_OFFBOARD:
            self.get_logger().info("Requesting Offboard mode and Arming...")
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
            self.publish_trajectory_setpoint(0.0, 0.0, 0.0)
        
        elif self.flight_time < 10.0:
            self.publish_trajectory_setpoint(0.0, 0.0, self.takeoff_height)
            self.flight_time += self.dt
            if int(self.flight_time * 10) % 20 == 0:
                self.get_logger().info(f"Hovering at {abs(self.takeoff_height)}m...")

        else:
            self.get_logger().info("Landing...")
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
            self.timer.cancel() 

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
        msg = VehicleCommand()
        msg.command, msg.param1, msg.param2 = command, p1, p2
        msg.target_system, msg.target_component = 1, 1
        msg.source_system, msg.source_component = 1, 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = OffboardControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
