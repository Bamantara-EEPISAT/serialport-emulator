#!/usr/bin/env python3
"""
CanSat Simulator - Compatible with Flutter Ground Station
Sends telemetry in CSV format matching the expected header
"""

import serial
import time
import random
import math
from datetime import datetime

class CanSatSimulator:
    """CanSat simulator that sends CSV telemetry data"""
    
    # Flight states
    STATES = [
        "LAUNCH_PAD",
        "ASCENT", 
        "APOGEE",
        "DESCENT",
        "PROBE_RELEASE",
        "PAYLOAD_RELEASE",
        "LANDED"
    ]
    
    # Paraglider states
    PG_STATES = [
        "_PG_CRUISE",
        "_PG_APPROACH",
        "_PG_LOITER",
        "_PG_FINAL",
        "_PG_FLARE",
        "_PG_LANDED"
    ]
    
    def __init__(self, port, baudrate=115200):
        """Initialize the simulator"""
        self.port = serial.Serial(port, baudrate, timeout=1)
        print(f"✅ Connected to {port} at {baudrate} baud")
        
        # Flight parameters
        self.team_id = "1064"
        self.packet_count = 0
        self.flight_mode = False
        self.telemetry_enabled = False
        self.simulation_enabled = False
        
        # Base coordinates (Surabaya area)
        self.base_lat = -7.275764
        self.base_lon = 112.794317
        self.max_drift_km = 2.0
        
        # Mission time
        self.mission_start = None
        
        # Command echo
        self.cmd_echo = "CXON"
        
        # Send header on startup
        self.send_header()
        
    def send_header(self):
        """Send CSV header"""
        header = (
            "TEAM_ID,MISSION_TIME,PACKET_COUNT,MODE,STATE,ALTITUDE,TEMPERATURE,PRESSURE,VOLTAGE,CURRENT,"
            "GYRO_R,GYRO_P,GYRO_Y,ACCEL_R,ACCEL_P,ACCEL_Y,GPS_TIME,GPS_ALTITUDE,"
            "GPS_LATITUDE,GPS_LONGITUDE,GPS_SATS,CMD_ECHO,,ROLL,PITCH,YAW,HEADING_ERROR,PG_STATE,"
            "DISTANCE_TO_TARGET,GROUND_DETECTION_ALTITUDE"
        )
        self.port.write((header + "\r\n").encode('utf-8'))
        print("📋 CSV Header sent")
        
    def get_mission_time(self):
        """Get mission time in HH:MM:SS format"""
        if self.mission_start is None:
            return "00:00:00"
        
        elapsed = int((datetime.now() - self.mission_start).total_seconds())
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_flight_state(self):
        """Determine current flight state based on packet count"""
        if not self.flight_mode:
            return "LAUNCH_PAD"
        
        t = self.packet_count
        if t <= 5:
            return "LAUNCH_PAD"
        elif t <= 30:
            return "ASCENT"
        elif t <= 40:
            return "APOGEE"
        elif t <= 65:
            return "DESCENT"
        elif t <= 70:
            return "PROBE_RELEASE"
        elif t <= 75:
            return "PAYLOAD_RELEASE"
        else:
            return "LANDED"
    
    def get_pg_state(self):
        """Get paraglider state"""
        if not self.flight_mode:
            return "_PG_CRUISE"
        
        t = self.packet_count
        if t <= 40:
            return "_PG_CRUISE"
        elif t <= 55:
            return "_PG_APPROACH"
        elif t <= 65:
            return "_PG_LOITER"
        elif t <= 70:
            return "_PG_FINAL"
        elif t <= 75:
            return "_PG_FLARE"
        else:
            return "_PG_LANDED"
    
    def get_altitude(self):
        """Generate realistic altitude profile"""
        if not self.flight_mode:
            return round(random.uniform(0.0, 0.5), 1)
        
        t = self.packet_count
        max_alt = 700.0
        
        # Ascent phase (0-30s)
        if t <= 30:
            progress = t / 30.0
            altitude = max_alt * (progress ** 1.5)
            altitude += random.uniform(-5.0, 5.0)
        # Apogee phase (30-40s)
        elif t <= 40:
            altitude = max_alt + random.uniform(-10.0, 10.0)
        # Descent phase (40-80s)
        elif t <= 80:
            descent_progress = (t - 40) / 40.0
            altitude = max_alt * (1.0 - descent_progress ** 2)
            altitude = max(0.0, altitude + random.uniform(-8.0, 8.0))
        # Landed
        else:
            altitude = random.uniform(0.0, 1.0)
        
        return round(max(0.0, altitude), 1)
    
    def get_gps_coordinates(self):
        """Generate GPS coordinates with drift during flight"""
        if self.flight_mode:
            drift_factor = min(self.packet_count / 100.0, 1.0)
            radius = (self.max_drift_km * drift_factor) / 111.0
        else:
            radius = 0.0001  # Small variation on launch pad
        
        angle = random.uniform(0, 2 * math.pi)
        offset = random.uniform(0, radius)
        lat_offset = offset * math.cos(angle)
        lon_offset = offset * math.sin(angle) / math.cos(math.radians(self.base_lat))
        
        lat = self.base_lat + lat_offset
        lon = self.base_lon + lon_offset
        
        return round(lat, 6), round(lon, 6)
    
    def get_orientation(self):
        """Generate roll, pitch, yaw values"""
        if self.flight_mode and self.packet_count > 5 and self.packet_count < 75:
            # Active flight - more dynamic
            roll = random.uniform(-45.0, 45.0)
            pitch = random.uniform(-30.0, 30.0)
            yaw = random.uniform(0.0, 360.0)
        else:
            # On ground - stable
            roll = random.uniform(-2.0, 2.0)
            pitch = random.uniform(-2.0, 2.0)
            yaw = random.uniform(0.0, 360.0)
        
        return round(roll, 1), round(pitch, 1), round(yaw, 1)
    
    def generate_telemetry(self):
        """Generate complete telemetry packet"""
        mission_time = self.get_mission_time()
        mode = "F" if self.flight_mode else "S"
        state = self.get_flight_state()
        
        # Sensor data
        altitude = self.get_altitude()
        temperature = round(random.uniform(5.0, 35.0), 1)
        pressure = round(random.uniform(85.0, 103.0), 1)
        voltage = round(random.uniform(3.5, 4.2), 1)
        current = round(random.uniform(0.10, 0.50), 2)
        
        # IMU data
        if self.flight_mode and state in ["ASCENT", "APOGEE", "DESCENT"]:
            gyro_r = round(random.uniform(-50.0, 50.0), 1)
            gyro_p = round(random.uniform(-50.0, 50.0), 1)
            gyro_y = round(random.uniform(-50.0, 50.0), 1)
            accel_r = round(random.uniform(-10.0, 10.0), 1)
            accel_p = round(random.uniform(-10.0, 10.0), 1)
            accel_y = round(random.uniform(-10.0, 10.0), 1)
        else:
            gyro_r = round(random.uniform(-2.0, 2.0), 1)
            gyro_p = round(random.uniform(-2.0, 2.0), 1)
            gyro_y = round(random.uniform(-2.0, 2.0), 1)
            accel_r = round(random.uniform(-0.5, 0.5), 1)
            accel_p = round(random.uniform(-0.5, 0.5), 1)
            accel_y = round(random.uniform(9.5, 10.5), 1)
        
        # GPS data
        gps_time = mission_time
        gps_altitude = round(altitude + random.uniform(-10.0, 10.0), 1)
        gps_lat, gps_lon = self.get_gps_coordinates()
        gps_sats = random.randint(4, 12)
        
        # Orientation
        roll, pitch, yaw = self.get_orientation()
        heading_error = round(random.uniform(-15.0, 15.0), 1)
        
        # Paraglider state
        pg_state = self.get_pg_state()
        distance_to_target = round(random.uniform(0.0, 1000.0), 1)
        ground_detection_alt = round(altitude + random.uniform(-5.0, 5.0), 1)
        
        # Build CSV line
        csv_line = (
            f"{self.team_id},"           # TEAM_ID
            f"{mission_time},"            # MISSION_TIME
            f"{self.packet_count},"       # PACKET_COUNT
            f"{mode},"                    # MODE
            f"{state},"                   # STATE
            f"{altitude},"                # ALTITUDE
            f"{temperature},"             # TEMPERATURE
            f"{pressure},"                # PRESSURE
            f"{voltage},"                 # VOLTAGE
            f"{current},"                 # CURRENT
            f"{gyro_r},"                  # GYRO_R
            f"{gyro_p},"                  # GYRO_P
            f"{gyro_y},"                  # GYRO_Y
            f"{accel_r},"                 # ACCEL_R
            f"{accel_p},"                 # ACCEL_P
            f"{accel_y},"                 # ACCEL_Y
            f"{gps_time},"                # GPS_TIME
            f"{gps_altitude},"            # GPS_ALTITUDE
            f"{gps_lat},"                 # GPS_LATITUDE
            f"{gps_lon},"                 # GPS_LONGITUDE
            f"{gps_sats},"                # GPS_SATS
            f"{self.cmd_echo},"           # CMD_ECHO
            f","                          # Empty field (double comma)
            f"{roll},"                    # ROLL
            f"{pitch},"                   # PITCH
            f"{yaw},"                     # YAW
            f"{heading_error},"           # HEADING_ERROR
            f"{pg_state},"                # PG_STATE
            f"{distance_to_target},"      # DISTANCE_TO_TARGET
            f"{ground_detection_alt}"     # GROUND_DETECTION_ALTITUDE
        )
        
        return csv_line
    
    def send_telemetry(self):
        """Generate and send telemetry packet"""
        csv_line = self.generate_telemetry()
        self.port.write((csv_line + "\r\n").encode('utf-8'))
        
        # Log to console
        print(f"📤 Packet {self.packet_count}: {csv_line[:80]}...")
        
        self.packet_count += 1
    
    def process_command(self, cmd_line):
        """Process incoming commands from ground station"""
        print(f"📥 Received: {cmd_line}")
        
        parts = cmd_line.strip().split(',')
        if len(parts) < 3:
            return
        
        if parts[0] != "CMD":
            return
        
        # team_id = parts[1]
        command = parts[2].upper()
        
        if command == "CX":
            # Toggle telemetry
            if len(parts) >= 4:
                mode = parts[3].upper()
                if mode == "ON":
                    self.telemetry_enabled = True
                    self.mission_start = datetime.now()
                    self.packet_count = 0
                    self.cmd_echo = "CXON"
                    print("📡 Telemetry ON")
                elif mode == "OFF":
                    self.telemetry_enabled = False
                    self.flight_mode = False
                    self.cmd_echo = "CXOFF"
                    print("📡 Telemetry OFF")
        
        elif command == "FLY":
            self.flight_mode = True
            self.telemetry_enabled = True
            self.mission_start = datetime.now()
            self.packet_count = 0
            self.cmd_echo = "FLY"
            print("🚀 Flight mode activated!")
        
        elif command == "CAL":
            self.packet_count = 0
            self.cmd_echo = "CAL"
            print("🔧 Calibration command received")
        
        elif command == "SIM":
            if len(parts) >= 4:
                sim_mode = parts[3].upper()
                if sim_mode == "ENABLE":
                    self.simulation_enabled = True
                    self.cmd_echo = "SIMENABLE"
                    print("🎮 Simulation mode enabled")
                elif sim_mode == "DISABLE":
                    self.simulation_enabled = False
                    self.cmd_echo = "SIMDISABLE"
                    print("🎮 Simulation mode disabled")
        
        elif command == "SET_TARGET":
            if len(parts) >= 5:
                target_lat = parts[3]
                target_lon = parts[4]
                self.cmd_echo = "SETTARGET"
                print(f"🎯 Target set: {target_lat}, {target_lon}")
        
        else:
            self.cmd_echo = command
            print(f"❓ Unknown command: {command}")
    
    def check_commands(self):
        """Check for incoming commands"""
        if self.port.in_waiting > 0:
            try:
                line = self.port.readline().decode('utf-8').strip()
                if line:
                    self.process_command(line)
            except Exception as e:
                print(f"❌ Error reading command: {e}")
    
    def run(self):
        """Main loop"""
        print("\n🛰️  CanSat Simulator Running")
        print("📋 Waiting for commands...")
        print("   Send 'CMD,1000,CX,ON' to start telemetry")
        print("   Send 'CMD,1000,FLY' to start flight simulation")
        print("\nPress Ctrl+C to stop\n")
        
        try:
            while True:
                # Check for incoming commands
                self.check_commands()
                
                # Send telemetry if enabled
                if self.telemetry_enabled:
                    self.send_telemetry()
                    
                    # Auto-stop after landing
                    if self.flight_mode and self.get_flight_state() == "LANDED" and self.packet_count > 80:
                        print("🪂 Flight complete - telemetry stopped")
                        self.telemetry_enabled = False
                        self.flight_mode = False
                
                # Wait ~1 second for next packet (20 Hz would be 0.05s)
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Simulation stopped by user")
        finally:
            self.port.close()
            print("👋 Port closed")


if __name__ == "__main__":
    import sys
    
    # Configuration
    PORT = "COM1"  # Change this to match your port
    BAUDRATE = 115200
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    if len(sys.argv) > 2:
        BAUDRATE = int(sys.argv[2])
    
    print("=" * 60)
    print("  CanSat Telemetry Simulator")
    print("  Compatible with Flutter Ground Station")
    print("=" * 60)
    print(f"\n📡 Port: {PORT}")
    print(f"⚡ Baudrate: {BAUDRATE}")
    print("\nUsage: python cansat_simulator_new.py [PORT] [BAUDRATE]")
    print("Example: python cansat_simulator_new.py COM3 115200\n")
    
    try:
        simulator = CanSatSimulator(PORT, BAUDRATE)
        simulator.run()
    except serial.SerialException as e:
        print(f"\n❌ Serial port error: {e}")
        print("\n💡 Tips:")
        print("  - Check if the port name is correct")
        print("  - Make sure no other program is using the port")
        print("  - On Windows: Use COM1, COM3, etc.")
        print("  - On Linux: Use /dev/ttyUSB0, /dev/ttyACM0, etc.")
        print("  - On Linux: You may need to run 'sudo usermod -a -G dialout $USER' and reboot")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

