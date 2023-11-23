import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message

# Initialize the LED matrix
def init_matrix():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90)
    return device

def main():
    device = init_matrix()
    for bright in range(0,255,20):
        print(f'Testing brightness {bright}')
        device.contrast(bright)
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="black", fill="white")
        time.sleep(2)

if __name__ == "__main__":
    main()

