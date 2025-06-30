# Author(s): Dr. Patrick Lemoine

# GOAL:
# This program connects to a GPS receiver (Yocto-GPS or a system GPS) to determine 
# the user's current geographic position and altitude.
# It retrieves and parses satellite data to calculate the elevation 
# and azimuth of each visible satellite.
# For each satellite, the program estimates its approximate latitude, longitude, 
# and altitude in space using geometric calculations.
# It displays detailed information for each satellite, including signal strength 
# and whether it is used in the current position fix.
# The program supports both Yocto-GPS modules and standard serial GPS receivers, 
# adapting its data parsing accordingly.

import os
import sys
import math
import time
import threading
import numpy as np
from vpython import *
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), 'YoctoLib.python'))

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

# Global variables for filtering
SHOW_GPS = True
SHOW_GLONASS = True
SHOW_GALILEO = True
MIN_SIGNAL_STRENGTH = 0  # Minimum signal strength to display (0-100)
HIGHLIGHT_USED_IN_FIX = True

def usage():
    scriptname = os.path.basename(sys.argv[0])
    print("Usage:")
    print(f"{scriptname} <target>")
    print(f"{scriptname} any")
    print(f"{scriptname} --system-gps <serial_port>")
    print(f"{scriptname} --3d <target>  # Enable 3D visualization")
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
    """Parse NMEA GSV sentences and return dict {satellite_number: (elevation, azimuth)}."""
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

def create_sky_display():
    """Create 3D interactive celestial sphere with cardinal points"""
    scene = canvas(title="Celestial Sphere - Satellite Positions", 
                  width=1200, height=800,
                  background=color.black)
    scene.forward = vector(0, -0.3, -1)
    
    # Add filter controls
    scene.append_to_caption("\n\nFilter Options:\n")
    
    # Constellation filter checkboxes
    scene.append_to_caption("Constellations: ")
    gps_checkbox = checkbox(bind=toggle_gps, text="GPS", checked=SHOW_GPS)
    scene.append_to_caption(" ")
    glonass_checkbox = checkbox(bind=toggle_glonass, text="GLONASS", checked=SHOW_GLONASS)
    scene.append_to_caption(" ")
    galileo_checkbox = checkbox(bind=toggle_galileo, text="GALILEO", checked=SHOW_GALILEO)
    scene.append_to_caption("\n")
    
    # Signal strength slider
    scene.append_to_caption("Min Signal Strength: ")
    signal_slider = slider(bind=update_min_signal, min=0, max=100, value=MIN_SIGNAL_STRENGTH, length=200)
    scene.append_to_caption("\n")
    
    # Used in fix checkbox
    scene.append_to_caption("Highlight satellites used in fix: ")
    used_checkbox = checkbox(bind=toggle_highlight_used, text="", checked=HIGHLIGHT_USED_IN_FIX)
    scene.append_to_caption("\n\n")
    
    # Celestial sphere with star texture
    celestial_sphere = sphere(radius=100, 
                             opacity=0.05, 
                             texture=textures.stars)
    
    # Cardinal points
    compass_points = [
        {"pos": vector(0, 0, 110), "label": "NORTH", "color": color.red},
        {"pos": vector(0, 0, -110), "label": "SOUTH", "color": color.green},
        {"pos": vector(110, 0, 0), "label": "EAST", "color": color.blue},
        {"pos": vector(-110, 0, 0), "label": "WEST", "color": color.yellow}
    ]
    
    for point in compass_points:
        text(pos=point["pos"], 
             text=point["label"], 
             height=5, 
             color=point["color"],
             align='center')
        arrow(pos=vector(0,0,0),
              axis=point["pos"],
              shaftwidth=0.5,
              color=point["color"])
    
    # Reference stars
    for _ in range(200):
        pos = vector(np.random.uniform(-100, 100),
                     np.random.uniform(-100, 100),
                     np.random.uniform(-100, 100))
        if mag(pos) > 95:  # Only place stars on sphere surface
            sphere(pos=pos, radius=0.3, color=color.white, emissive=True)
    
    # Store orbit tracks
    scene.orbit_tracks = {}
    
    return scene

def toggle_gps(checkbox):
    global SHOW_GPS
    SHOW_GPS = checkbox.checked

def toggle_glonass(checkbox):
    global SHOW_GLONASS
    SHOW_GLONASS = checkbox.checked

def toggle_galileo(checkbox):
    global SHOW_GALILEO
    SHOW_GALILEO = checkbox.checked

def update_min_signal(slider):
    global MIN_SIGNAL_STRENGTH
    MIN_SIGNAL_STRENGTH = slider.value

def toggle_highlight_used(checkbox):
    global HIGHLIGHT_USED_IN_FIX
    HIGHLIGHT_USED_IN_FIX = checkbox.checked

def should_display_satellite(sat_type, signal_strength, used_in_fix):
    """Determine if satellite should be displayed based on filter settings"""
    # Check constellation filter
    if sat_type == 0 and not SHOW_GPS:
        return False
    if sat_type == 1 and not SHOW_GLONASS:
        return False
    if sat_type == 2 and not SHOW_GALILEO:
        return False
    
    # Check signal strength
    if signal_strength < MIN_SIGNAL_STRENGTH:
        return False
    
    return True

def get_satellite_color(sat_type, signal_strength, used_in_fix):
    """Determine satellite color based on type and whether it's used in fix"""
    # Base colors for different constellations
    base_colors = {
        0: vector(0.8, 0.4, 0.0),  # GPS: orange
        1: vector(0.0, 0.6, 0.8),  # GLONASS: blue
        2: vector(0.0, 0.8, 0.2),  # GALILEO: green
    }
    
    base_color = base_colors.get(sat_type, vector(0.7, 0.7, 0.7))  # Default: gray
    
    # Highlight satellites used in fix
    if HIGHLIGHT_USED_IN_FIX and used_in_fix:
        return vector(1.0, 1.0, 0.0)  # Yellow for satellites used in fix
    
    return base_color

def get_satellite_size(signal_strength):
    """Determine satellite size based on signal strength"""
    # Scale size from 1 to 3 based on signal strength (0-100)
    min_size = 1.0
    max_size = 3.0
    if signal_strength <= 0:
        return min_size
    return min_size + (max_size - min_size) * (signal_strength / 100.0)

def update_satellites(scene, satellites_data):
    """Update satellite positions in the 3D view"""
    if not hasattr(scene, 'sat_objects'):
        scene.sat_objects = {}
    
    # Track which satellites are still visible
    visible_sats = set()
    
    # Update or create satellites
    for sat in satellites_data:
        sat_id = sat["id"]
        sat_type = sat.get("type", 0)  # Default to GPS if not specified
        signal = sat.get("signal", 50)  # Default to 50 if not specified
        used = sat.get("used", False)
        
        # Apply filters
        if not should_display_satellite(sat_type, signal, used):
            # Hide this satellite if it exists
            if sat_id in scene.sat_objects:
                scene.sat_objects[sat_id]['sphere'].visible = False
                scene.sat_objects[sat_id]['label'].visible = False
                if sat_id in scene.orbit_tracks:
                    scene.orbit_tracks[sat_id].visible = False
            continue
        
        visible_sats.add(sat_id)
        
        elev = math.radians(sat["elevation"])
        azim = math.radians(sat["azimuth"])
        
        # Convert spherical coordinates to Cartesian
        x = 100 * math.cos(elev) * math.sin(azim)
        y = 100 * math.sin(elev)
        z = 100 * math.cos(elev) * math.cos(azim)
        
        # Determine satellite color and size
        sat_color = get_satellite_color(sat_type, signal, used)
        sat_size = get_satellite_size(signal)
        
        if sat_id in scene.sat_objects:
            # Update existing satellite
            scene.sat_objects[sat_id]['sphere'].pos = vector(x, y, z)
            scene.sat_objects[sat_id]['sphere'].radius = sat_size
            scene.sat_objects[sat_id]['sphere'].color = sat_color
            scene.sat_objects[sat_id]['sphere'].visible = True
            
            scene.sat_objects[sat_id]['label'].pos = vector(x, y, z)
            scene.sat_objects[sat_id]['label'].text = f"{sat['name']}\nSig: {signal}"
            scene.sat_objects[sat_id]['label'].visible = True
            
            # Update orbit track
            update_orbit_track(scene, sat_id, sat)
        else:
            # Create new satellite
            sat_sphere = sphere(pos=vector(x, y, z),
                               radius=sat_size,
                               color=sat_color,
                               emissive=True)
            
            sat_label = label(pos=vector(x, y, z),
                             text=f"{sat['name']}\nSig: {signal}",
                             height=1.5,
                             border=4,
                             box=False)
            
            scene.sat_objects[sat_id] = {
                'sphere': sat_sphere,
                'label': sat_label
            }
            
            # Create orbit track
            create_orbit_track(scene, sat_id, sat)
    
    # Hide satellites that are no longer visible
    for sat_id in list(scene.sat_objects.keys()):
        if sat_id not in visible_sats:
            scene.sat_objects[sat_id]['sphere'].visible = False
            scene.sat_objects[sat_id]['label'].visible = False
            if sat_id in scene.orbit_tracks:
                scene.orbit_tracks[sat_id].visible = False

def create_orbit_track(scene, sat_id, sat_data):
    """Create a predicted orbit track for a satellite"""
    # Get current position
    elev = math.radians(sat_data["elevation"])
    azim = math.radians(sat_data["azimuth"])
    
    # Generate orbit points (simplified circular orbit)
    orbit_points = []
    
    # Create points for a simple circular orbit
    # In a real implementation, you would use orbital mechanics and TLE data
    # This is a simplified version that creates a circle on the celestial sphere
    num_points = 50
    
    # Create a circle perpendicular to the current position vector
    pos_vector = vector(
        100 * math.cos(elev) * math.sin(azim),
        100 * math.sin(elev),
        100 * math.cos(elev) * math.cos(azim)
    )
    
    # Create a perpendicular vector for the orbit plane
    # This is a simplified approach - real orbits would use actual orbital parameters
    if abs(pos_vector.y) < 0.9:  # Not near poles
        perp_vector = vector(pos_vector.z, 0, -pos_vector.x).norm()
    else:
        perp_vector = vector(1, 0, 0)  # Default for near-polar positions
    
    # Create another perpendicular vector to form a plane
    third_vector = cross(pos_vector, perp_vector).norm()
    
    # Create orbit points
    for i in range(num_points + 1):
        angle = i * 2 * math.pi / num_points
        # Rotate around the position vector
        point = 100 * (perp_vector * math.cos(angle) + third_vector * math.sin(angle))
        orbit_points.append(point)
    
    # Create the orbit curve
    sat_type = sat_data.get("type", 0)
    orbit_colors = {
        0: vector(0.8, 0.4, 0.0, 0.5),  # GPS: orange with transparency
        1: vector(0.0, 0.6, 0.8, 0.5),  # GLONASS: blue with transparency
        2: vector(0.0, 0.8, 0.2, 0.5),  # GALILEO: green with transparency
    }
    orbit_color = orbit_colors.get(sat_type, vector(0.7, 0.7, 0.7, 0.5))
    
    orbit_track = curve(pos=orbit_points, color=orbit_color, radius=0.5)
    scene.orbit_tracks[sat_id] = orbit_track

def update_orbit_track(scene, sat_id, sat_data):
    """Update the orbit track for a satellite"""
    # For this simplified implementation, we'll just ensure the track is visible
    if sat_id in scene.orbit_tracks:
        scene.orbit_tracks[sat_id].visible = True
    else:
        create_orbit_track(scene, sat_id, sat_data)

def run_yocto_gps(target, enable_3d=False):
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
    
    # Initialize 3D visualization if enabled
    scene = None
    if enable_3d:
        scene = create_sky_display()
    
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
        
        satellites_data = []
        for i in range(satCount):
            satInfo = gps.get_satelliteInfo(i)
            satType = satInfo.get_satType()
            satTypeStr = {0: "GPS", 1: "GLONASS", 2: "GALILEO"}.get(satType, "UNKNOWN")
            satID = satInfo.get_satNumber()
            signal = satInfo.get_signalStrength()
            used = satInfo.get_inUse()
            
            elevation_deg, azimuth_deg = sat_angles.get(satID, (None, None))
            if elevation_deg is not None and azimuth_deg is not None:
                lat_sat, lon_sat, alt_sat = satellite_position(lat, lon, elevation_deg, azimuth_deg)
                print(f"Satellite {i+1}: Type={satTypeStr} ID={satID} Signal={signal} UsedInFix={used}")
                print(f" Elevation={elevation_deg}°, Azimuth={azimuth_deg}°")
                print(f" Approximate position: Lat={lat_sat:.6f}°, Lon={lon_sat:.6f}°, Alt={alt_sat*1000:.0f} m")
                print("-----")
                
                satellites_data.append({
                    "id": satID,
                    "name": f"{satTypeStr}-{satID}",
                    "type": satType,
                    "elevation": elevation_deg,
                    "azimuth": azimuth_deg,
                    "signal": signal,
                    "used": used == 1
                })
        
        # Update 3D visualization
        if enable_3d and satellites_data:
            update_satellites(scene, satellites_data)
            rate(30)  # Limit to 30 FPS
        
        YAPI.Sleep(5000)
    
    YAPI.FreeAPI()

def run_system_gps(serial_port, baudrate=4800, enable_3d=False):
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
    
    # Initialize 3D visualization if enabled
    scene = None
    if enable_3d:
        scene = create_sky_display()
    
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
                                snr = int(fields[base_idx + 3]) if fields[base_idx + 3] else 0
                                sat_angles[sat_num] = (elevation, azimuth, snr)
                            except ValueError:
                                pass
            
            if receiver_lat is not None and receiver_lon is not None and sat_angles:
                print(f"Satellites visible: {len(sat_angles)}")
                satellites_data = []
                
                for sat_num, (elev, az, snr) in sat_angles.items():
                    lat_sat, lon_sat, alt_sat = satellite_position(receiver_lat, receiver_lon, elev, az)
                    print(f"Satellite {sat_num}: Elevation={elev}°, Azimuth={az}°, SNR={snr}")
                    print(f" Approximate position: Lat={lat_sat:.6f}°, Lon={lon_sat:.6f}°, Alt={alt_sat*1000:.0f} m")
                    
                    # Determine satellite type based on ID range (simplified)
                    sat_type = 0  # Default to GPS
                    if 65 <= sat_num <= 96:  # GLONASS range
                        sat_type = 1
                    elif 201 <= sat_num <= 252:  # GALILEO range
                        sat_type = 2
                    
                    satellites_data.append({
                        "id": sat_num,
                        "name": f"SAT-{sat_num}",
                        "type": sat_type,
                        "elevation": elev,
                        "azimuth": az,
                        "signal": snr,
                        "used": False  # We don't know which are used from GSV alone
                    })
                
                # Update 3D visualization
                if enable_3d and satellites_data:
                    update_satellites(scene, satellites_data)
                    rate(30)  # Limit to 30 FPS
            
            time.sleep(0.1)
        
        except pynmea2.ParseError:
            continue
        except KeyboardInterrupt:
            print("Exiting system GPS reader")
            break

def main():
    enable_3d = '--3d' in sys.argv
    if enable_3d:
        sys.argv.remove('--3d')  # Remove 3D flag from arguments
    
    if len(sys.argv) < 2:
        usage()
    
    if sys.argv[1] == '--system-gps':
        if len(sys.argv) < 3:
            print("Please specify serial port for system GPS, e.g. /dev/ttyUSB0 or COM3")
            sys.exit(1)
        serial_port = sys.argv[2]
        run_system_gps(serial_port, enable_3d=enable_3d)
        return
    
    if not YOCTO_AVAILABLE:
        print("Yocto libraries not found. Falling back to system GPS is recommended.")
        usage()
    
    target = sys.argv[1]
    try:
        run_yocto_gps(target, enable_3d=enable_3d)
    except Exception as e:
        print(f"Yocto-GPS error: {e}")
        print("Falling back to system GPS is recommended.")
        usage()

if __name__ == "__main__":
    main()
