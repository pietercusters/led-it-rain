import bluetooth
import time

known_devices = ["84:8C:8D:D2:16:D6"]  # Replace with your phone's Bluetooth MAC addresses

def find_nearby_devices():
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    return [address for address, name in nearby_devices]

def main():
    while True:
        found_devices = find_nearby_devices()
        if any(device in known_devices for device in found_devices):
            print("Ole's iphone detected!")
            pass
        else:
            print("Ole's iphone not detected!")
            pass
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()


