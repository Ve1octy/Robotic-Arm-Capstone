import pigpio
import time

# Define GPIO pin
SERVO_PIN = 18  # Use a hardware PWM-capable GPIO pin (12, 13, 18, or 19)

# Servo PWM settings
PWM_FREQUENCY = 50  # Standard servo frequency (Hz)
MIN_PULSE_WIDTH = 500   # 500μs (0° position)
MAX_PULSE_WIDTH = 2500  # 2500μs (270° position)
PWM_RANGE = 20000  # Total period (1s / 50Hz = 20ms or 20000μs)

# Initialize pigpio
pi = pigpio.pi()

if not pi.connected:
    print("Failed to connect to pigpio daemon")
    exit()

# Set hardware PWM
pi.hardware_PWM(SERVO_PIN, PWM_FREQUENCY, 0)  # Start with 0% duty cycle

def set_servo_angle(angle):
    """
    Set the servo to a specific angle between 0° and 270°.
    """
    #30 to 210 since realistically only have 180 deg to work with
    if angle < 30 or angle > 210:
        print("Angle out of range. Must be between 0 and 270 degrees.")
        return

    pulse_width = int(MIN_PULSE_WIDTH + (angle / 270.0) * (MAX_PULSE_WIDTH - MIN_PULSE_WIDTH))
    
    # Convert pulse width to duty cycle percentage (1% = 10000 in pigpio hardware_PWM)
    duty_cycle = int((pulse_width / PWM_RANGE) * 1000000)  # Convert to nanoseconds
    print(f"Setting angle: {angle} -> Pulse Width: {pulse_width}us -> Duty Cycle: {duty_cycle}")
    pi.hardware_PWM(SERVO_PIN, PWM_FREQUENCY, duty_cycle)

try:
    print("Moving to 90 degrees...")
    set_servo_angle(120)
    time.sleep(1)  # Wait for the servo to reach position

    # print("Moving to 65 degrees and stopping...")
    # set_servo_angle(30)
    # time.sleep(3)  # Wait for the servo to reach position

except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    pi.hardware_PWM(SERVO_PIN, PWM_FREQUENCY, 0)  # Stop servo
    pi.stop()
