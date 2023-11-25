import requests
from datetime import datetime
import pdb
import time

def get_rain(lat, lng):
    # pings the Buienradar API to get the predicted amount of rain for lat, lng
    # see also https://www.buienradar.nl/overbuienradar/gratis-weerdata

    #import random
    #rain = [random.randrange(9) for _ in range(0, 24)]
    #return rain
    
    #return range(0, 9)

    url = f'https://gpsgadget.buienradar.nl/data/raintext/?lat={lat}&lon={lng}'
    
    r = requests.get(url)

    data = r.text.split()
    current_time = datetime.now()
    rain_intensities = []
    max_intensity = 0

    for item in data:
        intensity_str, time_str = item.split('|')
        intensity = int(intensity_str)
        rain_mm_h = 10 ** ((intensity - 109) / 32.0)

        # Parse time
        pdb.set_trace()
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

def main():
    LAT = 52.353681668987726
    LNG = 4.92548286993842
    
    print('Polling API')
    LED_status = get_rain(LAT, LNG)
    print(LED_status)


if __name__ == "__main__":
    main()

