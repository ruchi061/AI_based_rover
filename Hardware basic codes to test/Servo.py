import time
import board
import busio
import curses
from adafruit_pca9685 import PCA9685
# Initialize I2C and PCA9685
i2c = busio.I2C(board.SCL, board.SDA)
pwm = PCA9685(i2c)
pwm.frequency = 50 # Standard servo frequency
# Servo angle limits
SERVO_MIN = 2000 # Adjust as needed
SERVO_MAX = 8000 # Adjust as needed
# Servo channels to be controlled
73
IITE/CSE2025/UDP112 Software Implementation
ACTIVE_CHANNELS = [0, 1, 2, 3, 4,5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
# Function to convert angle to duty cycle
def set_servo_angle(channel, angle):
 """Convert servo angle (0-180) to PWM duty cycle and set it."""
 angle = max(0, min(180, angle)) # Keep angle in range
 pulse = int(SERVO_MIN + (angle / 180.0) * (SERVO_MAX - SERVO_MIN))
 pwm.channels[channel].duty_cycle = pulse
# Initialize all active servos to 90 degrees
servo_angles = {ch: 90 for ch in ACTIVE_CHANNELS}
for ch in ACTIVE_CHANNELS:
 set_servo_angle(ch, 90)
def main(stdscr):
 """Curses-based control loop."""
 curses.cbreak()
 stdscr.keypad(True)
 stdscr.nodelay(True) # Non-blocking key detection
 stdscr.clear()
 try:
 while True:
 key = stdscr.getch()
 # Increase angle for all servos
 if key == curses.KEY_UP:
 for ch in ACTIVE_CHANNELS:
 servo_angles[ch] = min(180, servo_angles[ch] + 5)
 set_servo_angle(ch, servo_angles[ch])
74
IITE/CSE2025/UDP112 Software Implementation
 # Decrease angle for all servos
 elif key == curses.KEY_DOWN:
 for ch in ACTIVE_CHANNELS:
 servo_angles[ch] = max(0, servo_angles[ch] - 5)
 set_servo_angle(ch, servo_angles[ch])
 elif key == ord('w'):
 for ch in ACTIVE_CHANNELS:
 servo_angles[ch] = 180
 set_servo_angle(ch, servo_angles[ch])
 elif key == ord('s'):
 for ch in ACTIVE_CHANNELS:
 servo_angles[ch] = 90
 set_servo_angle(ch, servo_angles[ch])
 elif key == ord('d'):
 for ch in ACTIVE_CHANNELS:
 servo_angles[ch] = 0
 set_servo_angle(ch, servo_angles[ch])
 except KeyboardInterrupt:
 pass # Allow graceful exit
 finally:
 pwm.deinit() # Reset PCA9685
 curses.endwin() # Restore terminal settings
# Run the curses application
curses.wrapper(main)
"""
75
IITE/CSE2025/UDP112 Software Implementation
PCI9685 pin connection of part servo 
PIN 0 = top-left wheel
PIN 1 = top-right wheel
PIN 2 = midel-left wheel
PIN 3 = midel-right wheel
PIN 4 = bottom-left wheel
PIN 5 = bottom-right wheel
PIN 6 = shoulder-of-arm
PIN 7 = elbow-of-arm
PIN 8 = grip
PIN 9 = pi-camera-holder-used to move camera 0-180
"""
