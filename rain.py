import requests
from datetime import datetime

def get_rain(lat, lng):
    '''
    pings the Buienradar API to get the predicted amount of rain for lat, lng
    see also https://www.buienradar.nl/overbuienradar/gratis-weerdata
    returns the rain intensities for the next 2 hours in 5mins slots, scaled
    on a scale from 0-8 (number of LEDs to light up) based on a max of 2.5mm/h,
    or the max of the series of rain data
    '''

    url = f'https://gpsgadget.buienradar.nl/data/raintext/?lat={lat}&lon={lng}'

    r = requests.get(url)

    data = r.text.split()
    current_time = datetime.now()
    rain_intensities = []
    print(data)

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

    max_intensity = max(4.0, max(rain_intensities))
    scaled_intensities = [round(rain/max_intensity*8) for rain in rain_intensities]

    return scaled_intensities


def main():
    LAT = 52.353681668987726
    LNG = 4.92548286993842

    print('Polling API')
    rain_intensities = get_rain(LAT, LNG)
    print(scaled_intensities)


if __name__ == "__main__":
    main()

