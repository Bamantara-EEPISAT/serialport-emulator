import csv
import random
from datetime import timedelta
from constants import TEAM_ID, START_TIME, STATES, altitude_values, temperature_range, pressure_range, voltage_range, gyro_range, accel_range, mag_range, rotation_rate_range, gps_altitude_range, latitude_range, longitude_range, gps_sats_range, commands

# Set year
year = 2025

# Checksum calculation functions
def buatcs(data_str):
    hasil = 0
    for char in data_str[:150]:  # Process up to 150 characters
        hasil += ord(char)  # Add ASCII value of each character
        if char == '\0':    # Stop if a null character is encountered
            break
    return hasil & 0xFFFF  # Return as a 16-bit result

# Generating telemetry data
telemetry_data = []
current_time = START_TIME
packet_count = 0

for i in range(55):
    state = STATES[min(i // 10, len(STATES) - 1)]  # Move through states
    packet_count += 1
    mission_time = current_time.strftime("%H:%M:%S")
    gps_time = mission_time  # Simulated GPS time as mission time

    # Generate data for each field
    row = {
        "TEAM_ID": TEAM_ID,
        "MISSION_TIME": mission_time,
        "PACKET_COUNT": packet_count,
        "MODE": "F",
        "STATE": state,
        "ALTITUDE": round(random.uniform(*altitude_values[state]), 1),
        "TEMPERATURE": round(random.uniform(*temperature_range), 1),
        "PRESSURE": round(random.uniform(*pressure_range), 1),
        "VOLTAGE": round(random.uniform(*voltage_range), 2),
        "GYRO_R": round(random.uniform(*gyro_range), 2),
        "GYRO_P": round(random.uniform(*gyro_range), 2),
        "GYRO_Y": round(random.uniform(*gyro_range), 2),
        "ACCEL_R": round(random.uniform(*accel_range), 2),
        "ACCEL_P": round(random.uniform(*accel_range), 2),
        "ACCEL_Y": round(random.uniform(*accel_range), 2),
        "MAG_R": round(random.uniform(*mag_range), 2),
        "MAG_P": round(random.uniform(*mag_range), 2),
        "MAG_Y": round(random.uniform(*mag_range), 2),
        "AUTO_GYRO_ROTATION_RATE": random.randint(*rotation_rate_range),
        "GPS_TIME": gps_time,
        "GPS_ALTITUDE": round(random.uniform(*gps_altitude_range), 2),
        "GPS_LATITUDE": round(random.uniform(*latitude_range), 4),
        "GPS_LONGITUDE": round(random.uniform(*longitude_range), 4),
        "GPS_SATS": random.randint(*gps_sats_range),
        "CMD_ECHO": commands[1] if state == "LAUNCH_PAD" and packet_count == 0 else commands[0],
        "": ""
    }

    # Serialize row to a string format for checksum calculation
    data_str = ",".join(str(value) for value in row.values())
    data_str = data_str + ","
    cst = buatcs(data_str)
    cs1 = cst & 0xFF
    cs2 = (cst >> 8) & 0xFF
    checksum = ~(cs1 + cs2) & 0xFF
    row["CHECKSUM"] = checksum

    telemetry_data.append(row)
    current_time += timedelta(seconds=1)  # Increment time by one second

# Writing to CSV
with open(f"telemetry_data_{year}.csv", "w", newline="") as csvfile:
    fieldnames = row.keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in telemetry_data:
        writer.writerow(data)

print(f"Telemetry data for {year} with checksums saved to telemetry_data_{year}.csv")
