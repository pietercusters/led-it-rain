from datetime import datetime
HEAVY = 2.5

def parse_rain_data(data):
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

    # scale everything on scale of 2.5mm/h (or the max of the rain intensities) and multiply by 8 to get to scale of 0-8
    rain_levels = [int(round(x/max(max_intensity, HEAVY)*8)) for x in rain_intensities]

    return rain_levels

# Example usage
data = ["077|23:55", "120|23:00", "122|23:05", "110|23:05"]  # Sample data
print(parse_rain_data(data))
