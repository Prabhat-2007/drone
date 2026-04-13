#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class HumanDetector(Node):
    def __init__(self):
        super().__init__('human_detector_node')
        
        # Load Pretrained YOLOv8 model (Nano version for speed)
        self.model = YOLO('yolov8n.pt') 
        self.bridge = CvBridge()
        
        # Publisher for detection results
        self.publisher_ = self.create_publisher(Point, '/human_detection', 10)
        
        # Subscriber for camera (Adjust topic name to match your 'ros2 topic list')
        self.subscription = self.create_subscription(
            Image,
            '/camera', 
            self.image_callback,
            10)
        
        self.get_logger().info('YOLO Human Detector Node Started')

    def image_callback(self, msg):
        try:
            # 1. Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # 2. Run YOLO Inference (classes=[0] is 'person' in COCO)
            results = self.model(cv_image, classes=[0], conf=0.5, verbose=False)
            
            # 3. Process Results
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    # Get coordinates
                    x1, y1, x2, y2 = box.xyxy[0]
                    conf = float(box.conf[0])
                    
                    # Calculate Center
                    cx = float((x1 + x2) / 2)
                    cy = float((y1 + y2) / 2)
                    
                    # 4. Publish Detection
                    detection_msg = Point()
                    detection_msg.x = cx
                    detection_msg.y = cy
                    detection_msg.z = conf # Using Z for confidence per your request
                    self.publisher_.publish(detection_msg)
                    
                    # 5. Draw for Visualization
                    cv2.rectangle(cv_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(cv_image, f"Human: {conf:.2f}", (int(x1), int(y1)-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the processed frame
            cv2.imshow("YOLO Detection Stream", cv_image)
            cv2.waitKey(1)
            
        except Exception as e:
            self.get_logger().error(f'Detection Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = HumanDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
