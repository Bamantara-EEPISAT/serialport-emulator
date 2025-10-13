from datetime import datetime

def load_constants(year):
    constants = {
        2025: {
            "TEAM_ID": "3121",
            "PACKET_COUNT_START": 0,
            "START_TIME": datetime(2025, 11, 14, 13, 0, 0),
            "STATES": ["LAUNCH_PAD", "ASCENT", "APOGEE", "DESCENT", "PROBE_RELEASE", "LANDED"],
            "altitude_values": {
                "LAUNCH_PAD": (0, 0.1),
                "ASCENT": (10, 1000),
                "APOGEE": (1000, 1100),
                "DESCENT": (500, 1000),
                "PROBE_RELEASE": (50, 500),
                "LANDED": (0, 0.1),
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
            "commands": ["CXON", "CAL"],
        },

        2026: {
            "TEAM_ID": "3121",
            "PACKET_COUNT_START": 0,
            "START_TIME": datetime(2026, 11, 14, 13, 0, 0),
            "STATES": ["LAUNCH_PAD", "ASCENT", "APOGEE", "DESCENT", "PROBE_RELEASE", "PAYLOAD_RELEASE", "LANDED"],
            "altitude_values": {
                "LAUNCH_PAD": (0, 0.1),
                "ASCENT": (10, 1200),
                "APOGEE": (1000, 1200),
                "DESCENT": (500, 1200),
                "PROBE_RELEASE": (50, 600),
                "PAYLOAD_RELEASE": (50, 600),
                "LANDED": (0, 0.1),
            },
            "temperature_range": (-5.0, 40.0),
            "pressure_range": (80.0, 120.0),
            "voltage_range": (3.5, 4.2),
            "current_range": (1.5, 3.2),
            "gyro_range": (-5.0, 5.0),
            "accel_range": (-2.0, 2.0),
            "mag_range": (-1.0, 1.0),
            "rotation_rate_range": (0, 360),
            "gps_altitude_range": (0, 1200),
            "latitude_range": (-90.0, 90.0),
            "longitude_range": (-180.0, 180.0),
            "gps_sats_range": (3, 12),
            "commands": ["CXON", "CAL"],
        },
    }

    return constants.get(year, constants[2026])
