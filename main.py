import requests, re, logging
from logging.handlers import RotatingFileHandler
import sys
from time import sleep
from PIL import Image, ImageDraw


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s : %(message)s', handlers=[logging.handlers.RotatingFileHandler('log/buien.log', maxBytes=2e6, backupCount=5)])
    logging.info('Started')

    im = Image.new('1', (32, 8))
    draw = ImageDraw.Draw(im)

    # input lat & long from address here
    lat = 52.353681668987726
    lng = 4.92548286993842

    attempts = 5

    # try to get rain data
    for i in range(attempts):
        logging.info(f'Getting rain data - attempt {i+1}/{attempts}')
        rain = get_rain(lat, lng)
        if rain is not None:
            for idx, level in enumerate(rain):
                draw.line((8+idx, 8-level, 8+idx, 8), fill=255)
            break
        sleep(2)

    # try to get temp data
    for i in range(attempts):
        logging.info(f'Getting temp data - attempt {i+1}/{attempts}')
        temp = get_temp(lat, lng)
        if temp is not None:
            if len(temp) == 1:
                draw = draw_digit(temp, draw, 3)
            elif len(temp) == 2:
                draw = draw_digit(temp[0], draw)
                draw = draw_digit(temp[1], draw, 4)

            else: # double digit freezing
                draw = draw_digit('-', draw)
                draw = draw_digit('-', draw, 4)
            break
        sleep(2) 

    im = im.resize((640, 160))
    im.show()

    logging.info('Finished')

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

    temp = str(round(r.json()['main']['feels_like']))
    logging.info(f'Retrieved temp data from openwheather - feels like {temp}')

    return temp

def get_rain(lat, lng):
    # pings the Buienradar API to get the predicted amount of rain for lat, lng
    # see also https://www.buienradar.nl/overbuienradar/gratis-weerdata

    #import random
    #return [random.randrange(9) for _ in range(0, 24)]
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

    return rain

if __name__ == "__main__":
    main()
