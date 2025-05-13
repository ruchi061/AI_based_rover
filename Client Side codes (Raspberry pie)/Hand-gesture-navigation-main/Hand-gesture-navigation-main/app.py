import socket
import RPi.GPIO as GPIO
from adafruit_pca9685 import PCA9685
import board
import busio
from datetime import datetime
import time
# ========== STATUS LED ==========
STATUS_LED = 25
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(STATUS_LED, GPIO.OUT)
67
IITE/CSE2025/UDP112 Software Implementation
def blink_led():
 GPIO.output(STATUS_LED, GPIO.HIGH)
 time.sleep(0.1)
 GPIO.output(STATUS_LED, GPIO.LOW)
# ========== MOTOR SETUP ==========
IN1, IN2, IN3, IN4, ENA, ENB = 17, 27, 22, 23, 18, 24
GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB], GPIO.OUT)
pwmA = GPIO.PWM(ENA, 1000)
pwmB = GPIO.PWM(ENB, 1000)
pwmA.start(100)
pwmB.start(100)
def move_forward(): GPIO.output([IN1, IN3], GPIO.HIGH); GPIO.output([IN2, IN4], 
GPIO.LOW)
def move_backward(): GPIO.output([IN2, IN4], GPIO.HIGH); GPIO.output([IN1, IN3], 
GPIO.LOW)
def left_forward_right_backward(): 
 GPIO.output(IN1, GPIO.HIGH); GPIO.output(IN2, GPIO.LOW)
 GPIO.output(IN3, GPIO.LOW); GPIO.output(IN4, GPIO.HIGH)
def left_backward_right_forward(): 
 GPIO.output(IN1, GPIO.LOW); GPIO.output(IN2, GPIO.HIGH)
 GPIO.output(IN3, GPIO.HIGH); GPIO.output(IN4, GPIO.LOW)
def stop_motors(): GPIO.output([IN1, IN2, IN3, IN4], GPIO.LOW)
# ========== SERVO SETUP ==========
i2c = busio.I2C(board.SCL, board.SDA)
pwm = PCA9685(i2c)
pwm.frequency = 50
SERVO_MIN, SERVO_MAX = 2000, 8000
68
IITE/CSE2025/UDP112 Software Implementation
def set_servo_angles(angles):
 for i, angle in enumerate(angles):
 angle = max(0, min(180, angle))
 pulse = int(SERVO_MIN + (angle / 180.0) * (SERVO_MAX - SERVO_MIN))
 pwm.channels[i].duty_cycle = pulse
# ========== MOVEMENTS ==========
movements = {
 'forward': ([90]*6, move_forward),
 'backward': ([90]*6, move_backward),
 'tank_left': ([40]*3 + [140]*3, left_backward_right_forward),
 'tank_right': ([140]*3 + [40]*3, left_forward_right_backward),
 'soft_left': ([87]*3 + [93]*3, move_forward),
 'soft_right': ([93]*3 + [87]*3, move_forward),
 'crab_left': ([60]*3 + [120]*3, move_forward),
 'crab_right': ([120]*3 + [60]*3, move_forward),
 'rotate_cw': ([50]*3 + [130]*3, left_forward_right_backward),
 'rotate_ccw': ([130]*3 + [50]*3, left_backward_right_forward),
 'fwd_left': ([85]*3 + [95]*3, move_forward),
 'fwd_right': ([95]*3 + [85]*3, move_forward),
 'bwd_left': ([85]*3 + [95]*3, move_backward),
 'bwd_right': ([95]*3 + [85]*3, move_backward),
 'stop': ([90]*6, stop_motors),
}
# ========== UDP SERVER ==========
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 5005))
sock.settimeout(0.5)
69
IITE/CSE2025/UDP112 Software Implementation
connected = False
client_addr = None
try:
 print("?? Waiting for laptop connection...")
 while not connected:
 try:
 data, addr = sock.recvfrom(1024)
 if data.decode().strip() == "CONNECT_REQUEST":
 sock.sendto("CONNECTED".encode(), addr)
 client_addr = addr
 connected = True
 print(f"? Connected to laptop at {addr}")
 except socket.timeout:
 continue
 print("?? Ready to receive gestures. Press Ctrl+C to stop.")
 while True:
 try:
 data, addr = sock.recvfrom(1024)
 if addr != client_addr:
 print(f"?? Ignoring unknown sender: {addr}")
 continue
 gesture = data.decode().strip()
 current_time = datetime.now().strftime("%H:%M:%S")
 if gesture in movements:
 angles, motor_fn = movements[gesture]
70
IITE/CSE2025/UDP112 Software Implementation
 set_servo_angles(angles)
 motor_fn()
 blink_led()
 print(f"[{current_time}] ? Received gesture: {gesture}")
 else:
 print(f"[{current_time}] ? Unknown gesture: {gesture}")
 except socket.timeout:
 continue
except KeyboardInterrupt:
 print("\n?? Stopping...")
finally:
 sock.close()
 stop_motors()
 pwm.deinit()
 pwmA.stop()
 pwmB.stop()
 GPIO.cleanup()
 print("? GPIO cleanup complete.")
