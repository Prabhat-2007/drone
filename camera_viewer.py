#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraViewer(Node):
    def __init__(self):
        super().__init__('camera_viewer_node')
        
        # Initialize the CvBridge
        self.bridge = CvBridge()
        
        # Subscribe to the camera topic
        # Note: In Gazebo Harmonic/PX4, the topic might be /camera or /world/default/model/x500/link/base_link/sensor/camera/image
        # Adjust the topic name below based on your 'ros2 topic list' output
        self.subscription = self.create_subscription(
            Image,
            '/camera', 
            self.image_callback,
            10)
        self.get_logger().info('Camera Viewer Node Started. Waiting for stream...')

    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV image (BGR)
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Display the image in a window
            cv2.imshow("Drone Camera Stream", cv_image)
            
            # Refresh the window (1ms delay)
            cv2.waitKey(1)
            
        except Exception as e:
            self.get_logger().error(f'Could not convert image: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = CameraViewer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
