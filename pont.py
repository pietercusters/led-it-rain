import requests
from time import sleep
from datetime import datetime


def get_ferry_ETD():
    """
    Fetches the remaining time from the URL specified
    """

    url = "https://api.pontveer.nl/api/departures/?line=Azartplein%20(F1)%20-%20Zamenhofstraat%20(F1)"
    response = requests.get(url)
    now = datetime.now()
    if response.status_code == 200:
        data = response.json()
        ETD_str = data[0]['expected_departure_time']
        ETD = datetime.strptime(ETD_str, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
        return ETD

def main():

    while True:
        print("polling API...")
        ETD = get_ferry_ETD()
        now = datetime.now()
        diff = ETD - now
        minutes, seconds = divmod(abs(diff.total_seconds()), 60)
        time_remaining = "{:02d}:{:02d}".format(int(minutes), int(seconds))
        print(f"Expected departure in {time_remaining}")
        sleep(5)

if __name__ == "__main__":
    main()
