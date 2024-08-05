import time
import cv2
import numpy as np
from manevra_son import StopProcessing  # Ensure this is imported correctly


def detect_red_lines(image):
    # Convert the image to HSV format
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define the red color range
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)
    
    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)
    
    # Combine the two masks
    mask = mask1 + mask2
    
    return mask

def find_contours(mask):
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_line_position(contours, image_width):
    left_line = None
    right_line = None
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if x < image_width // 2:
            if left_line is None or x > left_line[0]:
                left_line = (x, y, w, h)
        else:
            if right_line is None or x < right_line[0]:
                right_line = (x, y, w, h)
    
    return left_line, right_line

def park_between_red_lines(camera, robot, park_boolean):
    start_time = time.time()  # Record the start time
    duration = 5

    while time.time() - start_time < duration:
        
        
        image = camera.value
        
        # Detect red lines
        mask = detect_red_lines(image)
        
        # Find contours
        contours = find_contours(mask)
        
        if len(contours) > 0:
            # Find line positions
            left_line, right_line = get_line_position(contours, image.shape[1])
            
            if left_line:
                # Draw the left line box
                cv2.rectangle(image, (left_line[0], left_line[1]), (left_line[0] + left_line[2], left_line[1] + left_line[3]), (0, 255, 0), 2)
            
            if right_line:
                # Draw the right line box
                cv2.rectangle(image, (right_line[0], right_line[1]), (right_line[0] + right_line[2], right_line[1] + right_line[3]), (0, 255, 0), 2)
                      
            
            if left_line and right_line:
                # If both lines are found, try to center
                x1 = (left_line[0] + right_line[0]) / 2
                y1 = (left_line[1] + right_line[1]) / 2
                
                x2 = (left_line[0] + left_line[2] + right_line[0] + right_line[2]) / 2
                y2 = (left_line[1] + left_line[3] + right_line[1] + right_line[3]) / 2
                
                # Calculate the midpoint of the dominant line
                line_center_x = (x1 + x2) / 2
                line_center_y = (y1 + y2) / 2
                
                if x2 - x1 != 0:
                    slope = (y2 - y1) / (x2 - x1)
                    angle = np.arctan(slope) * 180 / np.pi
                else:
                    angle = 90 if y2 > y1 else -90
                    
                height, width, channels = image.shape
                frame_center_x = width / 2
                
                
                # Determine the direction based on the line's position relative to the frame center
                if line_center_x < frame_center_x - 10:  # Threshold to avoid jitter
                    direction = 'left'
                elif line_center_x > frame_center_x + 10:
                    direction = 'right'
                else:
                    direction = 'straight'
                    
                
                # Step 8: Generate Control Signals
                if direction == 'left':
                    # turn left
                    left_motor_speed = 0.5
                    right_motor_speed = 1.0
                elif direction == 'right':
                    # turn right
                    left_motor_speed = 1.0
                    right_motor_speed = 0.5
                else:
                    # move straight
                    left_motor_speed = 1.0
                    right_motor_speed = 1.0

                # Adjust speed based on angle
                angle_threshold = 10  # degrees
                if abs(angle) > angle_threshold:
                    
                    if angle > 0:
                        left_motor_speed *= (abs(angle) / 90)
                    else:
                        right_motor_speed *= (abs(angle) / 90)
                        
                robot.left_motor.value = left_motor_speed * 0.27    
                robot.right_motor.value = right_motor_speed * 0.19
                    
            else:
                robot.stop()
                time.sleep(0.5)

        else:
            robot.stop()
            time.sleep(0.5)
          
        # Wait a bit before the next frame
        time.sleep(0.25)
        

    
    # Stop the robot after the loop ends
    robot.stop()
    park_boolean.append(False)
    raise StopProcessing  

