import serial
from datetime import datetime, timedelta
import time
import random
import math

# Load constants for 2026 mission
def load_constants(year):
    constants = {
        2026: {
            "TEAM_ID": "3121",
            "PACKET_COUNT_START": 0,
            "START_TIME": datetime(2026, 11, 15, 13, 0, 0),
            "STATES": ["LAUNCH_PAD", "ASCENT", "APOGEE", "DESCENT", "PROBE_RELEASE", "PAYLOAD_RELEASE", "LANDED"],
            "altitude_values": {
                "LAUNCH_PAD": (0.0, 0.5),
                "ASCENT": (10.0, 700.0),
                "APOGEE": (680.0, 720.0),
                "DESCENT": (300.0, 680.0),
                "PROBE_RELEASE": (100.0, 300.0),
                "PAYLOAD_RELEASE": (10.0, 100.0),
                "LANDED": (0.0, 1.0)
            },
            # Updated ranges with proper resolutions for 2026
            "temperature_range": (5.0, 35.0),      # °C, resolution 0.1
            "pressure_range": (85.0, 103.0),       # kPa, resolution 0.1  
            "voltage_range": (3.5, 4.2),           # V, resolution 0.1
            "current_range": (0.10, 0.50),         # A, resolution 0.01
            "gyro_range": (-50.0, 50.0),           # °/s for flight dynamics
            "accel_range": (-10.0, 10.0),          # m/s² for flight dynamics
            "gps_altitude_range": (0, 750),        # meters above MSL
            "gps_sats_range": (4, 12),
            "commands": ["CXON", "CAL", "FLY", "STGPS", "STUTC"]
        }
    }
    return constants.get(year, constants[2026])

class CanSatSimulator:
    command = ""
    flight_mode = False
    BASE_LAT = -7.275763964907654
    BASE_LON = 112.79431652372989
    MAX_DISTANCE_KM = 2.0  # Larger radius for realistic flight path

    def __init__(self, year, comport, baudrate, transmit_delim="\r\n", receive_delim="\r\n"):
        self.constants = load_constants(year)
        self.serial_port = serial.Serial(comport, baudrate, timeout=1)
        self.transmit_delim = transmit_delim
        self.receive_delim = receive_delim
        self.telemetry_on = False
        self.simulation_mode = False
        self.packet_count = self.constants["PACKET_COUNT_START"]
        self.state = "LAUNCH_PAD"
        self.last_transmission_time = datetime.now()
        self.cmd_echo = "CXON"  # Default command echo
        print(f"✅ CanSat 2026 Simulator initialized on {comport} at {baudrate} baud.")

    def send_command(self, command):
        """Send a command to the CanSat."""
        self.serial_port.write((command + self.transmit_delim).encode())
        print(f"Sent: {command}")

    def receive_data(self):
        """Receive data from the GCS."""
        if self.serial_port.in_waiting > 0:
            data = self.serial_port.readline().decode().strip()
            if data:
                print(f"Received: {data}")
                self.process_command(data)

    def process_command(self, data):
        """Process incoming commands and handle specific actions."""
        parts = data.split(",")
        if len(parts) < 3:
            print("Invalid command format")
            return

        # Extract command parts
        cmd_main = parts[2].strip().upper()
        cmd_tail = parts[3].strip().upper() if len(parts) >= 4 else ""
        
        # Set command echo (no commas in echo)
        if cmd_main == "CX" and cmd_tail:
            self.cmd_echo = f"{cmd_main}{cmd_tail}"
        else:
            self.cmd_echo = "".join(p.strip() for p in parts[2:])

        # Handle commands
        if cmd_main == "CX":
            self.handle_cx(cmd_tail)
        elif cmd_main == "FLY":
            self.handle_fly()
        elif cmd_main == "ST":
            self.handle_st(cmd_tail)
        elif cmd_main == "SIM":
            self.handle_sim(cmd_tail)
        elif cmd_main == "CAL":
            self.handle_cal()
        else:
            print(f"Unknown command: {cmd_main}")

    def handle_cx(self, on_off):
        """Turn telemetry on or off."""
        if on_off == "ON":
            self.telemetry_on = True
            self.flight_mode = False  # CX mode is not flight mode
            self.packet_count = 0
            print("📡 Telemetry transmission activated (CX mode).")
        elif on_off == "OFF":
            self.telemetry_on = False
            self.flight_mode = False
            print("📡 Telemetry transmission deactivated.")

    def handle_fly(self):
        """Start flight sequence."""
        if not self.telemetry_on:
            self.telemetry_on = True
            print("⚠️ Telemetry was OFF. Enabling automatically for flight.")
        
        self.flight_mode = True
        self.packet_count = 0
        print("🚀 Flight command received. Beginning flight sequence!")

    def handle_st(self, time_value):
        """Set mission time."""
        print(f"Mission time set to: {time_value}")

    def handle_sim(self, mode):
        """Handle simulation mode commands."""
        if mode == "ENABLE":    
            self.simulation_mode = True
            print("Simulation mode enabled.")
        elif mode == "ACTIVATE":
            print("Simulation mode activated.")
        elif mode == "DISABLE":
            self.simulation_mode = False
            print("Simulation mode disabled.")

    def handle_cal(self):
        """Calibrate altitude to zero."""
        self.packet_count = 0
        print("🔧 Altitude calibrated to zero.")

    def buatcs(self, data_str):
        """Calculate checksum sum - matching C# algorithm"""
        hasil = 0
        debug_chars = ''
        
        for i, char in enumerate(data_str[:200]):
            char_code = ord(char)
            hasil += char_code
            
            # Debug first 10 and last 10 characters
            if i < 10 or i >= len(data_str) - 10:
                debug_chars += f'{char}({char_code}) '
            elif i == 10:
                debug_chars += '... '
            
            if char == '\0':
                break
                
        print(f"Buat CS: {data_str} | Sum: {hasil}")
        print(f"   String length: {len(data_str)}")
        print(f"   First/Last chars: {debug_chars}")
        print(f"   Sum result: {hasil}")
        
        return hasil & 0xFFFF

    def random_coordinates(self):
        """Generate realistic flight path coordinates."""
        if self.flight_mode:
            # Simulate drift during flight
            drift_factor = min(self.packet_count / 100.0, 1.0)  # Increase drift over time
            radius = (self.MAX_DISTANCE_KM * drift_factor) / 111.0
        else:
            # Small variation on launch pad
            radius = 0.1 / 111.0
            
        angle = random.uniform(0, 2 * math.pi)
        offset = random.uniform(0, radius)
        lat_offset = offset * math.cos(angle)
        lon_offset = offset * math.sin(angle) / math.cos(math.radians(self.BASE_LAT))
        
        return round(self.BASE_LAT + lat_offset, 4), round(self.BASE_LON + lon_offset, 4)

    def get_flight_altitude(self):
        """Generate realistic flight altitude profile reaching ~700m apogee."""
        if not self.flight_mode:
            return round(random.uniform(0.0, 0.5), 1)
        
        t = self.packet_count
        # Flight phases: ascent 30s, apogee 10s, descent 40s
        ascent_duration = 30
        apogee_duration = 10
        descent_duration = 40
        total_flight = ascent_duration + apogee_duration + descent_duration
        
        max_altitude = 700.0
        
        if t <= ascent_duration:
            # Smooth ascent with some acceleration variation
            progress = t / ascent_duration
            altitude = max_altitude * (progress ** 1.5)  # Slightly curved ascent
            # Add some realistic noise
            altitude += random.uniform(-5.0, 5.0)
        elif t <= (ascent_duration + apogee_duration):
            # Apogee phase - near maximum with small variations
            altitude = max_altitude + random.uniform(-10.0, 10.0)
        elif t <= total_flight:
            # Descent phase
            descent_progress = (t - ascent_duration - apogee_duration) / descent_duration
            remaining_altitude = max_altitude * (1.0 - descent_progress ** 2)  # Accelerating descent
            altitude = max(0.0, remaining_altitude + random.uniform(-8.0, 8.0))
        else:
            # Landed
            altitude = random.uniform(0.0, 1.0)
            
        return round(max(0.0, altitude), 1)

    def update_flight_state(self):
        """Update flight state based on packet count and altitude."""
        if not self.flight_mode:
            self.state = "LAUNCH_PAD"
            return
            
        t = self.packet_count
        if t <= 5:
            self.state = "LAUNCH_PAD"
        elif t <= 30:
            self.state = "ASCENT"
        elif t <= 40:
            self.state = "APOGEE"
        elif t <= 65:
            self.state = "DESCENT"
        elif t <= 70:
            self.state = "PROBE_RELEASE"
        elif t <= 75:
            self.state = "PAYLOAD_RELEASE"
        else:
            self.state = "LANDED"

    def transmit_telemetry(self):
        """Transmit 2026 format telemetry data every 1 second."""
        current_time = datetime.now()
        if (current_time - self.last_transmission_time).total_seconds() < 1:
            return

        # Update state
        self.update_flight_state()
        
        # Stop flight if landed
        if self.flight_mode and self.state == "LANDED" and self.packet_count > 80:
            self.flight_mode = False
            self.telemetry_on = False
            print("🪂 Flight ended. Telemetry stopped.")
            return

        # Time data
        mission_time = current_time.strftime("%H:%M:%S")
        gps_time = mission_time

        # Location data
        lat, lon = self.random_coordinates()

        # Flight data with proper resolutions
        altitude = self.get_flight_altitude()
        temperature = round(random.uniform(*self.constants['temperature_range']), 1)
        pressure = round(random.uniform(*self.constants['pressure_range']), 1)
        voltage = round(random.uniform(*self.constants['voltage_range']), 1)
        current = round(random.uniform(*self.constants['current_range']), 2)

        # IMU data - more dynamic during flight, calm on ground
        if self.flight_mode and self.state in ["ASCENT", "APOGEE", "DESCENT"]:
            gyro_r = round(random.uniform(*self.constants['gyro_range']), 2)
            gyro_p = round(random.uniform(*self.constants['gyro_range']), 2)
            gyro_y = round(random.uniform(*self.constants['gyro_range']), 2)
            accel_r = round(random.uniform(*self.constants['accel_range']), 2)
            accel_p = round(random.uniform(*self.constants['accel_range']), 2)
            accel_y = round(random.uniform(*self.constants['accel_range']), 2)
        else:
            gyro_r = round(random.uniform(-2.0, 2.0), 2)
            gyro_p = round(random.uniform(-2.0, 2.0), 2)
            gyro_y = round(random.uniform(-2.0, 2.0), 2)
            accel_r = round(random.uniform(-0.5, 0.5), 2)
            accel_p = round(random.uniform(-0.5, 0.5), 2)
            accel_y = round(random.uniform(9.5, 10.5), 2)  # Gravity when static

        # GPS data
        gps_altitude = round(altitude + random.uniform(-10.0, 10.0), 1)
        gps_sats = random.randint(*self.constants['gps_sats_range'])

        # Mode
        mode = "F" if self.flight_mode else "S"

        # Build packet in exact 2026 format
        packet = (
            f"{self.constants['TEAM_ID']},{mission_time},{self.packet_count},{mode},{self.state},"
            f"{altitude},{temperature},{pressure},{voltage},{current},"
            f"{gyro_r},{gyro_p},{gyro_y},"
            f"{accel_r},{accel_p},{accel_y},"
            f"{gps_time},{gps_altitude},{lat},{lon},{gps_sats},"
            f"{self.cmd_echo},,"  # Two commas after CMD_ECHO as per spec
        )

        # Calculate checksum using original algorithm (JANGAN UBAH!)
        cst = self.buatcs(packet)
        cs1 = cst & 0xFF
        cs2 = (cst >> 8) & 0xFF
        checksum = ~(cs1 + cs2) & 0xFF
        
        # Debug logging (matching Flutter format)
        print(f"🔍 Python checksum calculation:")
        print(f"   Data: '{packet}'")
        print(f"   Data length: {len(packet)}")
        print(f"   Python buatcs(): {cst}")
        print(f"   cs1 (low): {cs1}, cs2 (high): {cs2}")
        print(f"   Expected checksum: ~({cs1} + {cs2}) & 0xFF = {checksum}")

        # Final packet
        full_packet = packet + f"{checksum}"

        # Transmit
        try:
            self.serial_port.write((full_packet + self.transmit_delim).encode('utf-8'))
            print(f"📤 Telemetry: {full_packet}")
        except Exception as e:
            print(f"Error transmitting: {e}")

        self.packet_count += 1
        self.last_transmission_time = current_time

    def start(self):
        """Main loop for receiving data and transmitting telemetry."""
        try:
            while True:
                self.receive_data()
                if self.telemetry_on:
                    self.transmit_telemetry()
                time.sleep(0.05)  # Short delay
        except KeyboardInterrupt:
            print("🛑 Simulation terminated by user.")
        finally:
            self.serial_port.close()

# Main execution
if __name__ == "__main__":
    year = 2026
    comport = "COM1"  # Change as needed
    baudrate = 19200
    transmit_delim = "\r\n"
    receive_delim = "\r\n"

    cansat = CanSatSimulator(year, comport, baudrate, transmit_delim, receive_delim)
    cansat.start()
