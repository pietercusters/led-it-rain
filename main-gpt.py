import requests, re, logging
from logging.handlers import RotatingFileHandler
import sys
import RPi.GPIO as GPIO
import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message

MOTION_SENSOR_PIN = 25  # GPIO pin number for the motion sensor
DISPLAY_DURATION = 300  # Duration to keep the display on after motion is detected, in seconds
    
# input lat & long from address here
LAT = 52.353681668987726
LNG = 4.92548286993842

ATTEMPTS = 3            # number of ATTEMPTS for each API
WAIT_API = 1            # time to wait between API pings, in seconds
WAIT_MOTION = 1         # time to wait between motion sensor polls, in seconds


# Initialize the LED matrix
def init_matrix():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90, brightness=0)
    return device

def init_motion_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s : %(message)s', handlers=[logging.handlers.RotatingFileHandler('log/buien.log', maxBytes=2e6, backupCount=1), logging.StreamHandler(sys.stdout)])
    logging.info('Started')

    device = init_matrix()
    #init_motion_sensor()

    last_motion_time = 0

    try:
        while True:
            if GPIO.input(MOTION_SENSOR_PIN):
                logging.info('Detected motion')
                last_motion_time = time.time()
                # Add the display update/drawing code here
                device.show()
                update_display(device)

            # Turn off the display if no motion for DISPLAY_DURATION
            if time.time() - last_motion_time > DISPLAY_DURATION:
                device.hide()

            time.sleep(WAIT_MOTION)

    except KeyboardInterrupt:
        GPIO.cleanup()

def update_display(device):
    with canvas(device) as draw:
        # try to get rain data
        for i in range(ATTEMPTS):
            logging.info(f'Getting rain data - attempt {i+1}/{ATTEMPTS}')
            rain = get_rain(lat, lng)
            if rain is not None:
                for idx, level in enumerate(rain):
                    draw.line((idx, 8-level, idx, 8), fill="white")
                break
            time.sleep(WAIT_API)

        # try to get temp data
        for i in range(ATTEMPTS):
            logging.info(f'Getting temp data - attempt {i+1}/{ATTEMPTS}')
            temp = get_temp(lat, lng)
            if temp is not None:
                if len(temp) == 1:
                    draw_digit(temp, draw, 27)
                elif len(temp) == 2:
                    draw_digit(temp[0], draw, 25)
                    draw_digit(temp[1], draw, 29)
                else: # double digit freezing -- show min min
                    draw_digit('-', draw, 25)
                    draw_digit('-', draw, 29)
                break
            time.sleep(WAIT_API) 

def get_temp(lat, lng):
    # pings openwheather API to get current temparature
    # see also https://openweathermap.org/current

    #return '-13'

    key = '78efb78287a0d947d2bf4726b4bb6f60'
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={key}&units=metric'

    try:
        r = requests.get(url)
    except Exception as e:
        logging.error(f'Could not connect to openwheather: {e}')
        return None

    temp = str(round(r.json()['main']['temp']))
    logging.info(f'Retrieved temp data from openweather')

    return temp

def get_rain(lat, lng):
    # pings the Buienradar API to get the predicted amount of rain for lat, lng
    # see also https://www.buienradar.nl/overbuienradar/gratis-weerdata

    #import random
    #rain = [random.randrange(9) for _ in range(0, 24)]
    #return rain
    
    #return range(0, 9)

    url = f'https://gpsgadget.buienradar.nl/data/raintext/?lat={lat}&lon={lng}'
    
    try:
        r = requests.get(url)
    except Exception as e:
        logging.error(f'Could not connect to buienradar: {e}')
        return None

    data = r.text.split()
    logging.info(f'Retrieved {len(data)} predictions on rain levels from Buienradar.nl')

    rain = [round(int(re.findall('(\d{3})\|\d{2}:\d{2}', x)[0])/28.3) for x in data]
    print(rain)

    return rain


def draw_digit(digit, draw, offset=0):
    # prints a digit of width 3 and height 8 with offset [offset] to [draw]

    if digit == '0':
        draw.line((offset, 0, offset+2, 0), fill=255)       # links-rechts boven
        draw.line((offset, 7, offset+2, 7), fill=255)       # links-rechts onder
        draw.line((offset, 0, offset, 7), fill=255)         # links onder-boven
        draw.line((offset+2, 0, offset+2, 7), fill=255)     # rechts onder-boven

    if digit == '1':
        draw.line((offset+2, 0, offset+2, 7), fill=255)     # rechts onder-boven

    if digit == '2':
        draw.line((offset, 0, offset+2, 0), fill=255)       # links-rechts boven
        draw.line((offset, 7, offset+2, 7), fill=255)       # links-rechts onder
        draw.line((offset, 3, offset+2, 3), fill=255)       # links-rechts mid
        draw.line((offset, 3, offset, 7), fill=255)         # links mid-onder   
        draw.line((offset+2, 0, offset+2, 3), fill=255)     # rechts mid-boven   

    if digit == '3':
        draw.line((offset+2, 0, offset+2, 7), fill=255)     # rechts onder-boven
        draw.line((offset, 0, offset+2, 0), fill=255)       # links-rechts boven
        draw.line((offset, 7, offset+2, 7), fill=255)       # links-rechts onder
        draw.line((offset, 3, offset+2, 3), fill=255)       # links-rechts mid

    if digit == '4':
        draw.line((offset, 3, offset+2, 3), fill=255)       # links-rechts mid
        draw.line((offset+2, 0, offset+2, 7), fill=255)     # rechts onder-boven
        draw.line((offset, 0, offset, 3), fill=255)         # links mid-boven   

    if digit == '5':
        draw.line((offset, 0, offset+2, 0), fill=255)       # links-rechts boven
        draw.line((offset, 7, offset+2, 7), fill=255)       # links-rechts onder
        draw.line((offset, 3, offset+2, 3), fill=255)       # links-rechts mid
        draw.line((offset, 0, offset, 3), fill=255)         # links mid-boven   
        draw.line((offset+2, 3, offset+2, 7), fill=255)     # rechts mid-onder   

    if digit == '6':
        draw.line((offset, 0, offset+2, 0), fill=255)       # links-rechts boven
        draw.line((offset, 7, offset+2, 7), fill=255)       # links-rechts onder
        draw.line((offset, 3, offset+2, 3), fill=255)       # links-rechts mid
        draw.line((offset+2, 3, offset+2, 7), fill=255)     # rechts mid-onder   
        draw.line((offset, 0, offset, 7), fill=255)         # links onder-boven
        
    if digit == '7':
        draw.line((offset+2, 0, offset+2, 7), fill=255)     # rechts onder-boven
        draw.line((offset, 0, offset+2, 0), fill=255)       # links-rechts boven

    if digit == '8':
        draw.line((offset, 0, offset+2, 0), fill=255)       # links-rechts boven
        draw.line((offset, 7, offset+2, 7), fill=255)       # links-rechts onder
        draw.line((offset, 0, offset, 7), fill=255)         # links onder-boven
        draw.line((offset+2, 0, offset+2, 7), fill=255)     # rechts onder-boven
        draw.line((offset, 3, offset+2, 3), fill=255)       # links-rechts mid
    
    if digit == '9':
        draw.line((offset, 0, offset+2, 0), fill=255)       # links-rechts boven
        draw.line((offset, 7, offset+2, 7), fill=255)       # links-rechts onder
        draw.line((offset, 3, offset+2, 3), fill=255)       # links-rechts mid
        draw.line((offset+2, 0, offset+2, 7), fill=255)     # rechts onder-boven
        draw.line((offset, 0, offset, 3), fill=255)         # links mid-boven   

    if digit == '-':
        draw.line((offset+1, 3, offset+2, 3), fill=255)       # links-rechts mid

    return draw


if __name__ == "__main__":
    main()

