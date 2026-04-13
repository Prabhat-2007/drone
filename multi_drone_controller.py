#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleStatus

class MultiDroneController(Node):
    def __init__(self):
        super().__init__('multi_drone_controller')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # --- Drone 1 Setup (Scout) ---
        self.pub_offboard1 = self.create_publisher(OffboardControlMode, '/drone1/fmu/in/offboard_control_mode', qos)
        self.pub_setpoint1 = self.create_publisher(TrajectorySetpoint, '/drone1/fmu/in/trajectory_setpoint', qos)
        self.pub_cmd1 = self.create_publisher(VehicleCommand, '/drone1/fmu/in/vehicle_command', qos)
        self.status1 = VehicleStatus()
        self.sub_status1 = self.create_subscription(VehicleStatus, '/drone1/fmu/out/vehicle_status_v1', self.cb_status1, qos)

        # --- Drone 2 Setup (Standby) ---
        self.pub_offboard2 = self.create_publisher(OffboardControlMode, '/drone2/fmu/in/offboard_control_mode', qos)
        self.pub_setpoint2 = self.create_publisher(TrajectorySetpoint, '/drone2/fmu/in/trajectory_setpoint', qos)
        self.pub_cmd2 = self.create_publisher(VehicleCommand, '/drone2/fmu/in/vehicle_command', qos)
        self.status2 = VehicleStatus()
        self.sub_status2 = self.create_subscription(VehicleStatus, '/drone2/fmu/out/vehicle_status_v1', self.cb_status2, qos)

        self.timer = self.create_timer(0.1, self.timer_callback)
        self.step = 0

    def cb_status1(self, msg): self.status1 = msg
    def cb_status2(self, msg): self.status2 = msg

    def publish_cmd(self, pub, cmd, p1=0.0, p2=0.0):
        msg = VehicleCommand(command=cmd, param1=p1, param2=p2, target_system=1, target_component=1, 
                             source_system=1, source_component=1, from_external=True)
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        pub.publish(msg)

    def timer_callback(self):
        # Heartbeats
        offboard_msg = OffboardControlMode(position=True, timestamp=int(self.get_clock().now().nanoseconds / 1000))
        self.pub_offboard1.publish(offboard_msg)
        self.pub_offboard2.publish(offboard_msg)

        # 1. Arming sequence
        if self.status1.nav_state != VehicleStatus.NAVIGATION_STATE_OFFBOARD:
            self.publish_cmd(self.pub_cmd1, VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
            self.publish_cmd(self.pub_cmd1, VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
        
        if self.status2.nav_state != VehicleStatus.NAVIGATION_STATE_OFFBOARD:
            self.publish_cmd(self.pub_cmd2, VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
            self.publish_cmd(self.pub_cmd2, VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)

        # 2. Independent Trajectories
        # Drone 1: Moving in a square pattern based on step count
        if self.step < 50:    wp1 = [2.0, 0.0, -5.0]
        elif self.step < 100: wp1 = [2.0, 2.0, -5.0]
        elif self.step < 150: wp1 = [0.0, 2.0, -5.0]
        else:                 wp1 = [0.0, 0.0, -5.0]

        # Drone 2: Static Standby Hover
        wp2 = [0.0, -2.0, -3.0] 

        self.pub_setpoint1.publish(TrajectorySetpoint(position=wp1, timestamp=int(self.get_clock().now().nanoseconds / 1000)))
        self.pub_setpoint2.publish(TrajectorySetpoint(position=wp2, timestamp=int(self.get_clock().now().nanoseconds / 1000)))
        
        self.step = (self.step + 1) % 200

def main():
    rclpy.init()
    rclpy.spin(MultiDroneController())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
