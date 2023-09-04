import nest_asyncio
import sqlite3
from datetime import datetime

# Nest Asyncio for nested event loops
nest_asyncio.apply()
from godirect import GoDirect

# Connect to the database
conn = sqlite3.connect('sensors.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS sensors
             (timestamp TEXT, description TEXT, value REAL)''')

godirect = GoDirect(use_ble=True, use_usb=False)
# Connect to the first found device
device = godirect.list_devices()[0]
device.open(auto_start=True)
device.enable_default_sensors()
# Enable force sensor
device.enable_sensors([5])
sensors = device.get_enabled_sensors()

try:
    while True:
        try:
            if device.read():
                for sensor in sensors:
                    # Get current time as datetime object
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                    # Insert data into database
                    c.execute("INSERT INTO sensors VALUES (?, ?, ?)",
                              (timestamp, sensor.sensor_description, sensor.value))
                    conn.commit()

                    # Print to console (optional)
                    print(sensor.sensor_description + ": " + str(sensor.value))
        except KeyboardInterrupt:
            break
finally:
    device.close()
    conn.close()
