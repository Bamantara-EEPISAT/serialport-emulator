from datetime import datetime

# Function to load constants based on the year
def load_constants(year):
    constants = {
        2025: {
            "TEAM_ID": "3121",  # Replace with your team ID
            "PACKET_COUNT_START": 0,
            "START_TIME": datetime(2025, 11, 14, 13, 0, 0),  # Starting time for 2025
            "STATES": ["LAUNCH_PAD", "ASCENT", "APOGEE", "DESCENT", "PROBE_RELEASE", "LANDED"],
            "altitude_values": {
                "LAUNCH_PAD": (0, 0.1),
                "ASCENT": (10, 1000),
                "APOGEE": (1000, 1100),
                "DESCENT": (500, 1000),
                "PROBE_RELEASE": (50, 500),
                "LANDED": (0, 0.1)
            },
            "temperature_range": (-5.0, 35.0),
            "pressure_range": (80.0, 120.0),
            "voltage_range": (3.5, 4.2),
            "gyro_range": (-5.0, 5.0),
            "accel_range": (-2.0, 2.0),
            "mag_range": (-1.0, 1.0),
            "rotation_rate_range": (0, 360),
            "gps_altitude_range": (0, 1000),
            "latitude_range": (-90.0, 90.0),
            "longitude_range": (-180.0, 180.0),
            "gps_sats_range": (3, 12),
            "commands": ["CXON", "CAL"]
        },
        # Add more years below by copying and adjusting the values
        2026: {
            "TEAM_ID": "1001",  # Replace with your team ID for 2026
            "PACKET_COUNT_START": 0,
            "START_TIME": datetime(2026, 11, 14, 13, 0, 0),  # Starting time for 2026
            "STATES": ["LAUNCH_PAD", "ASCENT", "APOGEE", "DESCENT", "PROBE_RELEASE", "LANDED"],
            "altitude_values": {
                "LAUNCH_PAD": (0, 0.1),
                "ASCENT": (10, 1200),
                "APOGEE": (1000, 1200),
                "DESCENT": (500, 1200),
                "PROBE_RELEASE": (50, 600),
                "LANDED": (0, 0.1)
            },
            "temperature_range": (-5.0, 40.0),
            "pressure_range": (80.0, 120.0),
            "voltage_range": (3.5, 4.2),
            "gyro_range": (-5.0, 5.0),
            "accel_range": (-2.0, 2.0),
            "mag_range": (-1.0, 1.0),
            "rotation_rate_range": (0, 360),
            "gps_altitude_range": (0, 1000),
            "latitude_range": (-90.0, 90.0),
            "longitude_range": (-180.0, 180.0),
            "gps_sats_range": (3, 12),
            "commands": ["CXON", "CAL"]
        },
        # You can continue adding more years with their respective constants here...
    }

    # Return constants for the requested year, default to 2025 if the year is not found
    return constants.get(year, constants[2025])

# Example usage:
year = 2025  # Can be dynamically set based on current year or input
config = load_constants(year)

# Access specific constants for the selected year
TEAM_ID = config["TEAM_ID"]
START_TIME = config["START_TIME"]
STATES = config["STATES"]
altitude_values = config["altitude_values"]
temperature_range = config["temperature_range"]
pressure_range = config["pressure_range"]
voltage_range = config["voltage_range"]
gyro_range = config["gyro_range"]
accel_range = config["accel_range"]
mag_range = config["mag_range"]
rotation_rate_range = config["rotation_rate_range"]
gps_altitude_range = config["gps_altitude_range"]
latitude_range = config["latitude_range"]
longitude_range = config["longitude_range"]
gps_sats_range = config["gps_sats_range"]
commands = config["commands"]
