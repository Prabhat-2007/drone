import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

class AltitudeNode(Node):
    def __init__(self):
        super().__init__('altitude_controller')
        
        self.altitude_pub = self.create_publisher(Float64, 'drone_altitude', 10)
        
        self.target_sub = self.create_subscription(
            Float64, 
            'target_altitude', 
            self.target_callback, 
            10)
        
        self.timer = self.create_timer(0.1, self.publish_altitude)
        
        self.current_alt = 0.0
        self.target_alt = 0.0
        self.get_logger().info('Altitude Node Started.')

    def target_callback(self, msg):
        self.target_alt = msg.data
        self.get_logger().info(f'New Target Received: {self.target_alt}m')

    def publish_altitude(self):
        # Simple logic: drift toward the target altitude
        diff = self.target_alt - self.current_alt
        self.current_alt += diff * 0.1 
        
        msg = Float64()
        msg.data = self.current_alt
        self.altitude_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AltitudeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
