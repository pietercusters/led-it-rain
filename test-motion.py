import RPi.GPIO as GPIO
import time

MOTION_SENSOR_PIN = 25  # GPIO pin number for the motion sensor

# Initialize GPIO for motion sensor
def init_motion_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN)

def main():
    init_motion_sensor()
    last_state = None


    try:
        print("Warming up...")
        time.sleep(5)
        while True:
            current_state = GPIO.input(MOTION_SENSOR_PIN)
            if current_state != last_state:
                last_state = current_state
                if current_state:
                    print(f"{time.ctime()}: Motion detected!")
                else:
                    print(f"{time.ctime()}: No motion detected.")
            time.sleep(0.5)  # Check every 0.5 seconds

    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
