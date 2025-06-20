# Author(s): Dr. Patrick Lemoine

import os
import sys
import math
import time
import threading

try:
    import pynmea2
except ImportError:
    print("Please install pynmea2: pip install pynmea2")
    sys.exit(1)

# Try importing Yoctopuce libraries
try:
    from yocto_api import *
    from yocto_gps import *
    YOCTO_AVAILABLE = True
except ImportError:
    YOCTO_AVAILABLE = False

def usage():
    scriptname = os.path.basename(sys.argv[0])
    print("Usage:")
    print(f"{scriptname} <serial_number>")
    print(f"{scriptname} <logical_name>")
    print(f"{scriptname} any")
    print(f"{scriptname} --system-gps <serial_port>  # fallback to system GPS on serial port")
    sys.exit()

def die(msg):
    sys.exit(msg + ' (check USB cable or serial port)')

def satellite_position(receiver_lat, receiver_lon, elevation_deg, azimuth_deg):
    earth_radius_km = 6371.0
    satellite_altitude_km = 20200.0  # typical GPS satellite altitude

    lat_rad = math.radians(receiver_lat)
    lon_rad = math.radians(receiver_lon)
    el_rad = math.radians(elevation_deg)
    az_rad = math.radians(azimuth_deg)

    r_sat = earth_radius_km + satellite_altitude_km
    r_rec = earth_radius_km  # ignoring receiver altitude for simplicity

    x_rec = r_rec * math.cos(lat_rad) * math.cos(lon_rad)
    y_rec = r_rec * math.cos(lat_rad) * math.sin(lon_rad)
    z_rec = r_rec * math.sin(lat_rad)

    x_dir = math.cos(el_rad) * math.cos(az_rad)
    y_dir = math.cos(el_rad) * math.sin(az_rad)
    z_dir = math.sin(el_rad)

    x_sat = x_rec + r_sat * (-math.sin(lon_rad) * x_dir - math.sin(lat_rad) * math.cos(lon_rad) * y_dir + math.cos(lat_rad) * math.cos(lon_rad) * z_dir)
    y_sat = y_rec + r_sat * (math.cos(lon_rad) * x_dir - math.sin(lat_rad) * math.sin(lon_rad) * y_dir + math.cos(lat_rad) * math.sin(lon_rad) * z_dir)
    z_sat = z_rec + r_sat * (math.cos(lat_rad) * y_dir + math.sin(lat_rad) * z_dir)

    hyp = math.sqrt(x_sat * x_sat + y_sat * y_sat)
    lat_sat = math.degrees(math.atan2(z_sat, hyp))
    lon_sat = math.degrees(math.atan2(y_sat, x_sat))
    alt_sat = math.sqrt(x_sat * x_sat + y_sat * y_sat + z_sat * z_sat) - earth_radius_km

    return lat_sat, lon_sat, alt_sat

def parse_gsv(nmea_lines):
    """
    Parse NMEA GSV sentences and return dict {satellite_number: (elevation, azimuth)}.
    """
    sat_angles = {}
    for line in nmea_lines:
        if not line.startswith('$') or 'GSV' not in line:
            continue
        fields = line.strip().split(',')
        try:
            total_msgs = int(fields[1])
            msg_num = int(fields[2])
            sats_in_view = int(fields[3])
        except (ValueError, IndexError):
            continue

        sat_data_start = 4
        while sat_data_start + 3 < len(fields):
            try:
                sat_num = int(fields[sat_data_start])
                elevation = int(fields[sat_data_start + 1])
                azimuth = int(fields[sat_data_start + 2])
                # SNR = fields[sat_data_start + 3] (not used)
                sat_angles[sat_num] = (elevation, azimuth)
            except ValueError:
                pass
            sat_data_start += 4
    return sat_angles

def run_yocto_gps(target):
    errmsg = YRefParam()
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        die("Yocto-API init error: " + errmsg.value)

    if target.lower() == 'any':
        gps = YGps.FirstGps()
        if gps is None:
            die('No Yocto-GPS module connected')
        m = gps.get_module()
        target = m.get_serialNumber()
    else:
        gps = YGps.FindGps(target + '.gps')

    if not gps.isOnline():
        die('Yocto-GPS device not connected')

    print("Using Yocto-GPS device:", target)

    while gps.isOnline():
        if gps.get_isFixed() != YGps.ISFIXED_TRUE:
            print("Waiting for GPS fix...")
            YAPI.Sleep(2000)
            continue

        lat = gps.get_latitude()
        lon = gps.get_longitude()
        alt = gps.get_altitude()
        print(f"Fixed position: Latitude={lat:.6f}°, Longitude={lon:.6f}°, Altitude={alt:.1f} m")

        nmea_messages = gps.get_nmeaMessages()
        sat_angles = parse_gsv(nmea_messages)

        satCount = gps.get_satelliteCount()
        print(f"Satellites visible: {satCount}")

        for i in range(satCount):
            satInfo = gps.get_satelliteInfo(i)
            satType = satInfo.get_satType()
            satTypeStr = {0:"GPS", 1:"GLONASS", 2:"GALILEO"}.get(satType, "UNKNOWN")
            satID = satInfo.get_satNumber()
            signal = satInfo.get_signalStrength()
            used = satInfo.get_inUse()

            elevation_deg, azimuth_deg = sat_angles.get(satID, (None, None))

            if elevation_deg is None or azimuth_deg is None:
                print(f"Satellite {satID}: elevation/azimuth angles not available")
            else:
                lat_sat, lon_sat, alt_sat = satellite_position(lat, lon, elevation_deg, azimuth_deg)
                print(f"Satellite {i+1}: Type={satTypeStr} ID={satID} Signal={signal} UsedInFix={used}")
                print(f"  Elevation={elevation_deg}°, Azimuth={azimuth_deg}°")
                print(f"  Approximate satellite position: Latitude={lat_sat:.6f}°, Longitude={lon_sat:.6f}°, Altitude={alt_sat*1000:.0f} m")

        print("-----")
        YAPI.Sleep(5000)

    YAPI.FreeAPI()

def run_system_gps(serial_port, baudrate=4800):
    import serial

    try:
        ser = serial.Serial(serial_port, baudrate, timeout=1)
        print(f"Opened system GPS on {serial_port} at {baudrate} baud")
    except Exception as e:
        die(f"Failed to open serial port {serial_port}: {e}")

    receiver_lat = None
    receiver_lon = None
    receiver_alt = None
    sat_angles = {}

    print("Reading system GPS NMEA sentences...")

    while True:
        try:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if not line:
                continue
            if not line.startswith('$'):
                continue

            msg = pynmea2.parse(line)

            if isinstance(msg, pynmea2.GGA):
                if msg.gps_qual > 0:
                    receiver_lat = msg.latitude if msg.lat_dir == 'N' else -msg.latitude
                    receiver_lon = msg.longitude if msg.lon_dir == 'E' else -msg.longitude
                    receiver_alt = msg.altitude  # meters
                    print(f"Fix: Lat={receiver_lat:.6f}, Lon={receiver_lon:.6f}, Alt={receiver_alt:.1f} m")
                else:
                    print("No GPS fix yet")

            elif isinstance(msg, pynmea2.GSV):
                # Update satellite angles
                for i in range(msg.num_sv_in_view):
                    fields = line.split(',')
                    # Satellite info starts at index 4, each satellite uses 4 fields
                    for sat_idx in range(4):
                        base_idx = 4 + sat_idx * 4
                        if base_idx + 3 < len(fields):
                            try:
                                sat_num = int(fields[base_idx])
                                elevation = int(fields[base_idx + 1])
                                azimuth = int(fields[base_idx + 2])
                                # snr = fields[base_idx + 3]
                                sat_angles[sat_num] = (elevation, azimuth)
                            except ValueError:
                                pass

                if receiver_lat is not None and receiver_lon is not None:
                    print(f"Satellites visible: {len(sat_angles)}")
                    for sat_num, (elev, az) in sat_angles.items():
                        lat_sat, lon_sat, alt_sat = satellite_position(receiver_lat, receiver_lon, elev, az)
                        print(f"Satellite {sat_num}: Elevation={elev}°, Azimuth={az}°")
                        print(f"  Approximate position: Lat={lat_sat:.6f}°, Lon={lon_sat:.6f}°, Alt={alt_sat*1000:.0f} m")
            time.sleep(0.1)

        except pynmea2.ParseError:
            continue
        except KeyboardInterrupt:
            print("Exiting system GPS reader")
            break

def main():
    if len(sys.argv) < 2:
        usage()

    if sys.argv[1] == '--system-gps':
        if len(sys.argv) < 3:
            print("Please specify serial port for system GPS, e.g. /dev/ttyUSB0 or COM3")
            sys.exit(1)
        serial_port = sys.argv[2]
        run_system_gps(serial_port)
        return

    if not YOCTO_AVAILABLE:
        print("Yocto libraries not found. Falling back to system GPS is recommended.")
        usage()

    target = sys.argv[1]

    try:
        run_yocto_gps(target)
    except Exception as e:
        print(f"Yocto-GPS error: {e}")
        print("Falling back to system GPS is recommended.")
        usage()

if __name__ == "__main__":
    main()

