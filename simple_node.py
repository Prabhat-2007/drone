import rclpy
from rclpy.node import Node
def main(args=None):
    rclpy.init(args=args)
    node = Node('simple_node')
    node.get_logger().info('Hello from nidar_ws!')
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()
