import requests
from time import sleep
from datetime import datetime


def fetch_ferry_time(url):
    """
    Fetches the remaining time from the URL specified
    """

    response = requests.get(url)
    now = datetime.now()
    if response.status_code == 200:
        data = response.json()
        ETD_str = data[0]['expected_departure_time']
        ETD = datetime.strptime(ETD_str, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
        diff = ETD - now
        minutes, seconds = divmod(abs(diff.total_seconds()), 60)
        return "{:02d}:{:02d}".format(int(minutes), int(seconds))

def main():
    url = "https://api.pontveer.nl/api/departures/?line=Azartplein%20(F1)%20-%20Zamenhofstraat%20(F1)"

    while True:
        print("polling API...")
        time_remaining = fetch_ferry_time(url)
        print(f"Expected departure in {time_remaining}")
        sleep(5)

if __name__ == "__main__":
    main()
