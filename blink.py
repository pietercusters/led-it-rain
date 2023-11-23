import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

# Initialize the LED matrix
def init_matrix():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90)
    return device

def blink_matrix(device, blink_times=5, on_time=1, off_time=1):
    for _ in range(blink_times):
        # Turn on all LEDs
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="white")
        time.sleep(on_time)

        # Turn off all LEDs
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="black", fill="black")
        time.sleep(off_time)

def main():
    device = init_matrix()
    blink_matrix(device)

if __name__ == "__main__":
    main()

