import requests
import logging
from logging.handlers import RotatingFileHandler
import sys
from time import sleep
from datetime import datetime
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from pont import get_ferry_ETD

# input lat & long from address here
LAT = 52.353681668987726
LNG = 4.92548286993842
UPDATE_INTERVAL = 60 * 5  # Refresh temp & ETD every 5 minutes
DISPLAY_INTERVAL = 1      # Update every second
HEAVY = 2.5

# Initialize the LED matrix
def init_matrix():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90, brightness=1)
    device.contrast(0)
    return device


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s : %(message)s', handlers=[logging.handlers.RotatingFileHandler('/home/pi/python/led-it-rain/log/buien.log', maxBytes=2e6, backupCount=1), logging.StreamHandler(sys.stdout)])
    logging.info('Started')

    device = init_matrix()
    last_update_time = None

    try:
        while True:
            current_time = datetime.now()
            if 7 <= current_time.hour < 23:
                # Update the display if it's between 07:00 and 23:00
                if not last_update_time or \
                        (current_time - last_update_time).total_seconds() \
                        > UPDATE_INTERVAL:

                    # get ferry ETD
                    if 7 <= current_time.hour <= 9:
                        ETD = get_ferry_ETD()
                    else:
                        ETD = None

                    # get weather data
                    temp = get_temp(LAT, LNG)
                    rain = None
                    # rain = get_rain(LAT, LNG)

                    last_update_time = current_time

                update_display(device, temp, ETD, rain)
                device.show()
                sleep(DISPLAY_INTERVAL)
            else:
                # Clear the display outside the specified time window
                device.hide()

                # wait 5mins to see if already time to rise & shine
                sleep(5*60)


    except KeyboardInterrupt:
        pass
    finally:
        # Clear the display when exiting the script
        logging.info('Stopping script')
        with canvas(device) as draw:
            device.hide()

def update_display(device, temp, ETD, rain):
    with canvas(device) as draw:
        # draw rain curve - disabled for now
        if rain is not None:
            for xpos, level in enumerate(rain):
                draw.line((xpos, 8-level, xpos, 8), fill="white")

        # draw temp
        if temp is not None:
            if len(temp) == 1:
                draw_digit(temp, draw, 27)
            elif len(temp) == 2:
                draw_digit(temp[0], draw, 25)
                draw_digit(temp[1], draw, 29)
            else: # double digit freezing -- show min min
                draw_digit('-', draw, 25)
                draw_digit('-', draw, 29)

        if ETD is not None:
            now = datetime.now()
            diff = ETD - now
            minutes, seconds = divmod(abs(diff.total_seconds()), 60)
            time_remaining = "{:02d}:{:02d}".format(int(minutes), int(seconds))
            for xpos, digit in time_remaining:
                draw_digit(digit, draw, (xpos*4)+3)


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
    current_time = datetime.now()
    rain_intensities = []
    max_intensity = 0

    for item in data:
        intensity_str, time_str = item.split('|')
        intensity = int(intensity_str)
        rain_mm_h = 10 ** ((intensity - 109) / 32.0)

        # Parse time
        time_slot = datetime.strptime(time_str, '%H:%M')
        time_slot = time_slot.replace(year=current_time.year, month=current_time.month, day=current_time.day)

        # Check if the time slot is in the future
        if time_slot > current_time:
            rain_intensities.append(rain_mm_h)
            max_intensity = max(rain_mm_h, max_intensity)

    print(rain_intensities)
    # scale everything on scale of 2.5mm/h (or the max of the rain intensities) and multiply by 8 to get to scale of 0-8
    rain_levels = [int(round(x/max(max_intensity, HEAVY)))*8 for x in rain_intensities]

    return rain_levels


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

    if digit == ':':
        draw.line((offset+1, 2, offset+1, 2), fill=255)       # links-rechts mid
        draw.line((offset+1, 4, offset+1, 4), fill=255)       # links-rechts mid

    return draw


if __name__ == "__main__":
    main()

