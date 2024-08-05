import RPi.GPIO as GPIO
import time
from jetbot import Camera, Robot
import cv2
import numpy as np
from IPython.display import display
import ipywidgets as widgets
from threading import Thread
# Import StopProcessing within this module
class StopProcessing(Exception):
    pass
class StopProcessing2(Exception):
    pass
from plaka_okuma_final import parking


def get_distance(TRIGGER_PIN,ECHO_PIN):
    GPIO.output(TRIGGER_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, GPIO.LOW)
    start_time = time.time()
    stop_time = time.time()
    
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()
    
    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()
    
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

# Function to find black lines in the frame
def find_lines(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
    edges = cv2.Canny(binary, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
    return lines

# Function to filter lines
def filter_lines(lines):
    if lines is None:
        return None
    lines = [line[0] for line in lines]
    return lines

# Function to calculate direction
def calculate_direction(lines, width, height, frame):
    dominant_line = None
    max_length = 0
    for line in lines:
        x1, y1, x2, y2 = line
        length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if length > max_length:
            max_length = length
            dominant_line = (x1, y1, x2, y2)
    
    if dominant_line is None:
        return None, None

    x1, y1, x2, y2 = dominant_line
    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    line_center_x = (x1 + x2) / 2
    frame_center_x = width / 2

    if x2 - x1 != 0:
        slope = (y2 - y1) / (x2 - x1)
        angle = np.arctan(slope) * 180 / np.pi
    else:
        angle = 90 if y2 > y1 else -90

    if line_center_x < frame_center_x - 10:
        direction = 'left'
    elif line_center_x > frame_center_x + 10:
        direction = 'right'
    else:
        direction = 'straight'

    return direction, angle

# Function to generate control signals
def generate_control_signals(direction, angle):
    if direction == 'left':
        left_motor_speed = 0.5
        right_motor_speed = 1.0
    elif direction == 'right':
        left_motor_speed = 1.0
        right_motor_speed = 0.5
    else:
        left_motor_speed = 1.0
        right_motor_speed = 1.0

    angle_threshold = 10
    if abs(angle) > angle_threshold:
        if angle > 0:
            left_motor_speed *= (abs(angle) / 90)
        else:
            right_motor_speed *= (abs(angle) / 90)

    return left_motor_speed, right_motor_speed

# Function to turn the robot
def turn_robot(degrees,robot):
    if degrees < 0:
        robot.left(0.1)
    else:
        robot.right(0.1)
    time.sleep(abs(degrees) / 90)  # Assuming 90 degrees turn takes 1 second
    robot.stop()

# Function to perform the sequence after detecting the wall
def perform_sequence(camera, robot, istenilen_plaka, park_boolean, park_numarası):
    
    try:
        start_time = time.time()
        while time.time() - start_time < 0.5:
            frame = camera.value 
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            lines = find_lines(frame)
            if lines is not None:
                filtered_lines = filter_lines(lines)
                height, width, channels = frame.shape
                direction, angle = calculate_direction(filtered_lines, width, height, frame)
                if direction is not None:
                    left_motor_speed, right_motor_speed = generate_control_signals(direction, angle)
                    robot.left_motor.value = left_motor_speed * 0.15
                    robot.right_motor.value = right_motor_speed * 0.15
        
        for _ in range(5):
            robot.stop()
            time.sleep(2)  # Wait for 2 seconds

            # Move straight for 1 seconds while tracking the line
            start_time = time.time()
            while time.time() - start_time < 0.65:
                frame = camera.value 
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                lines = find_lines(frame)
                if lines is not None:
                    filtered_lines = filter_lines(lines)
                    height, width, channels = frame.shape
                    direction, angle = calculate_direction(filtered_lines, width, height, frame)
                    if direction is not None:
                        left_motor_speed, right_motor_speed = generate_control_signals(direction, angle)
                        robot.left_motor.value = left_motor_speed * 0.15
                        robot.right_motor.value = right_motor_speed * 0.15
                else:
                    robot.stop()

            robot.stop()
            time.sleep(2)  # Wait for 2 seconds

            # Turn right 90 degrees
            turn_robot(100,robot)
            time.sleep(2)  # Wait for 2 seconds
            parking(istenilen_plaka, camera, robot, park_boolean,park_numarası)
            time.sleep(1)

            # Turn left 180 degrees
            turn_robot(-195,robot)
            time.sleep(2)  # Wait for 2 seconds
            parking(istenilen_plaka, camera, robot, park_boolean,park_numarası)
            time.sleep(1)

            # Turn right 90 degrees
            turn_robot(100,robot)
            time.sleep(2)  # Wait for 2 seconds

            # Move straight for 1 second while tracking the line
            start_time = time.time()
            while time.time() - start_time < 0.65:
                frame = camera.value
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                lines = find_lines(frame)
                if lines is not None:
                    filtered_lines = filter_lines(lines)
                    height, width, channels = frame.shape
                    direction, angle = calculate_direction(filtered_lines, width, height, frame)
                    if direction is not None:
                        left_motor_speed, right_motor_speed = generate_control_signals(direction, angle)
                        robot.left_motor.value = left_motor_speed * 0.15
                        robot.right_motor.value = right_motor_speed * 0.15
                else:
                    robot.stop()

            robot.stop()
            
    except StopProcessing:
        print("Plaka Bulundu excpt3")
        raise

# Function to update image and control robot
def update_image(search_mode, camera,robot, TRIGGER_PIN, ECHO_PIN, istenilen_plaka, park_boolean, park_numarası):
    
    try:
        frame = camera.value
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        distance = get_distance(TRIGGER_PIN,ECHO_PIN)
        count = 0

        if distance < 14:
            print(f"White wall detected at {distance:.2f} cm, initiating turn right procedure...")
            robot.right(0.15)  # Start turning right slowly
            time.sleep(1.1)  # Turn right for 1 second
            robot.stop()
            time.sleep(2)  # Wait for 2 seconds after stopping
            count =+ 1
            if count == 3:
                print("excpt6")
                raise StopProcessing2
                
            perform_sequence(camera, robot, istenilen_plaka, park_boolean, park_numarası)
            search_mode = True  # Start searching for the black line again
        else:
            if search_mode:
                lines = find_lines(frame)
                if lines is not None:
                    search_mode = False  # Exit search mode once lines are found
                    print("Black line found, switching to follow mode")
                else:
                    print("Searching for black line...")
                    robot.left_motor.value = 0.2
                    robot.right_motor.value = -0.2  # Rotate to search for the line
            else:
                lines = find_lines(frame)
                if lines is not None:
                    filtered_lines = filter_lines(lines)
                    height, width, channels = frame.shape
                    direction, angle = calculate_direction(filtered_lines, width, height, frame)
                    if direction is not None:
                        left_motor_speed, right_motor_speed = generate_control_signals(direction, angle)
                        print(f"Direction: {direction}, Angle: {angle}")
                        print(f"Left Motor Speed: {left_motor_speed}, Right Motor Speed: {right_motor_speed}")
                        robot.left_motor.value = left_motor_speed * 0.15
                        robot.right_motor.value = right_motor_speed * 0.15
                    else:
                        print("No dominant line detected")
                else:
                    print("No lines detected")       


        return search_mode
    
    except StopProcessing:
        print("Plaka Bulundu excpt4")
        raise

def run_loop(istenilen_plaka, park_boolean, park_numarası):
    
    try:
    
        # GPIO pin setup for ultrasonic sensor
        TRIGGER_PIN = 23
        ECHO_PIN = 24

        # GPIO setup
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(TRIGGER_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)

        # Initialize JetBot robot and camera
        robot = Robot()
        camera = Camera.instance(width=224, height=224)

        search_mode = True  # Start in search mode

        while 1:
            search_mode = update_image(search_mode, camera, robot,TRIGGER_PIN, ECHO_PIN, istenilen_plaka, park_boolean, park_numarası)
            time.sleep(0.1)  # Small delay to control the frame rate

    except StopProcessing:
        print("Plaka Bulundu")
        camera.stop() 
        robot.stop()
        print("Manevra stopped.")
        
        
    except StopProcessing2:
        camera.stop() 
        robot.stop()
        print("Manevra stopped.")
        raise