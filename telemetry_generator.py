import csv
import random
import math
from datetime import timedelta
from constants import load_constants

# === CONFIGURABLE ===
MISSION_YEAR = 2026  # Ubah ke 2025 atau 2026 sesuai misi
PACKET_COUNT_TOTAL = 55

# === LOAD CONSTANTS ===
config = load_constants(MISSION_YEAR)
TEAM_ID = config["TEAM_ID"]
START_TIME = config["START_TIME"]
STATES = config["STATES"]
altitude_values = config["altitude_values"]
temperature_range = config["temperature_range"]
pressure_range = config["pressure_range"]
voltage_range = config["voltage_range"]
gyro_range = config["gyro_range"]
accel_range = config["accel_range"]
gps_altitude_range = config["gps_altitude_range"]
latitude_range = config["latitude_range"]
longitude_range = config["longitude_range"]
gps_sats_range = config["gps_sats_range"]
commands = config["commands"]
rotation_rate_range = config.get("rotation_rate_range", (0, 360))
current_range = config.get("current_range", (0.0, 0.0))
mag_range = config.get("mag_range", None)  # None jika tidak ada magnetometer

# === BASE COORDINATES ===
BASE_LAT = -7.275823
BASE_LON = 112.794301
MAX_DISTANCE_KM = 0.5


# === CHECKSUM FUNCTION ===
def buatcs(data_str):
    hasil = 0
    for char in data_str[:150]:
        hasil += ord(char)
        if char == "\0":
            break
    return hasil & 0xFFFF


# === RANDOM COORDINATE GENERATOR ===
def random_coordinates():
    radius = MAX_DISTANCE_KM / 111.0
    angle = random.uniform(0, 2 * math.pi)
    offset = random.uniform(0, radius)
    lat_offset = offset * math.cos(angle)
    lon_offset = offset * math.sin(angle) / math.cos(math.radians(BASE_LAT))
    return round(BASE_LAT + lat_offset, 6), round(BASE_LON + lon_offset, 6)


# === FIELDNAME SELECTOR (auto menyesuaikan format tiap tahun) ===
def get_fieldnames(year: int):
    base = [
        "TEAM_ID", "MISSION_TIME", "PACKET_COUNT", "MODE", "STATE",
        "ALTITUDE", "TEMPERATURE", "PRESSURE", "VOLTAGE"
    ]

    # 2026 punya CURRENT
    if year >= 2026:
        base.append("CURRENT")

    # Gyro dan Accel wajib
    imu = [
        "GYRO_R", "GYRO_P", "GYRO_Y",
        "ACCEL_R", "ACCEL_P", "ACCEL_Y",
    ]

    # Magnetometer hanya jika ada (2025)
    if mag_range is not None and year < 2026:
        imu += ["MAG_R", "MAG_P", "MAG_Y"]

    gps = [
        "GPS_TIME", "GPS_ALTITUDE", "GPS_LATITUDE",
        "GPS_LONGITUDE", "GPS_SATS", "CMD_ECHO", "", "CHECKSUM"
    ]

    return base + imu + gps


# === TELEMETRY GENERATION ===
def generate_telemetry(year: int):
    telemetry_data = []
    current_time = START_TIME
    packet_count = 0
    fieldnames = get_fieldnames(year)

    for i in range(PACKET_COUNT_TOTAL):
        state = STATES[min(i // 10, len(STATES) - 1)]
        packet_count += 1
        mission_time = current_time.strftime("%H:%M:%S")
        gps_time = mission_time
        lat, lon = random_coordinates()

        # --- Base row ---
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
        }

        # --- Tambah CURRENT jika 2026 ---
        if "CURRENT" in fieldnames:
            row["CURRENT"] = round(random.uniform(*current_range), 2)

        # --- Gyro & Accel ---
        row.update({
            "GYRO_R": round(random.uniform(*gyro_range), 2),
            "GYRO_P": round(random.uniform(*gyro_range), 2),
            "GYRO_Y": round(random.uniform(*gyro_range), 2),
            "ACCEL_R": round(random.uniform(*accel_range), 2),
            "ACCEL_P": round(random.uniform(*accel_range), 2),
            "ACCEL_Y": round(random.uniform(*accel_range), 2),
        })

        # --- Magnetometer hanya jika ada ---
        if mag_range is not None and "MAG_R" in fieldnames:
            row.update({
                "MAG_R": round(random.uniform(*mag_range), 2),
                "MAG_P": round(random.uniform(*mag_range), 2),
                "MAG_Y": round(random.uniform(*mag_range), 2),
            })

        # --- GPS dan lainnya ---
        row.update({
            "GPS_TIME": gps_time,
            "GPS_ALTITUDE": round(random.uniform(*gps_altitude_range), 2),
            "GPS_LATITUDE": lat,
            "GPS_LONGITUDE": lon,
            "GPS_SATS": random.randint(*gps_sats_range),
            "CMD_ECHO": commands[1] if state == "LAUNCH_PAD" and packet_count == 0 else commands[0],
            "": ""
        })

        # --- Checksum ---
        data_str = ",".join(str(row.get(f, "")) for f in fieldnames if f not in ["CHECKSUM"])
        cst = buatcs(data_str + ",")
        cs1 = cst & 0xFF
        cs2 = (cst >> 8) & 0xFF
        checksum = ~(cs1 + cs2) & 0xFF
        row["CHECKSUM"] = checksum

        telemetry_data.append(row)
        current_time += timedelta(seconds=1)

    # === Write CSV ===
    filename = f"telemetry_data_{year}.csv"
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(telemetry_data)

    print(f"✅ Telemetry data for mission {year} saved to {filename}")


if __name__ == "__main__":
    generate_telemetry(MISSION_YEAR)
