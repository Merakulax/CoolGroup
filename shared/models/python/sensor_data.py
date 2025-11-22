"""
Sensor Data Models - Python
Auto-generated from contracts/sensor_data.json
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Accelerometer:
    x: float
    y: float
    z: float


@dataclass
class Gyroscope:
    x: float
    y: float
    z: float


@dataclass
class GPS:
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None


@dataclass
class SensorPayload:
    """Sensor data payload from Watch to Phone/Cloud"""
    heart_rate: int
    timestamp: int
    accelerometer: Optional[Accelerometer] = None
    gyroscope: Optional[Gyroscope] = None
    gps: Optional[GPS] = None
    barometer: Optional[float] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = {
            'heartRate': self.heart_rate,
            'timestamp': self.timestamp
        }
        if self.accelerometer:
            result['accelerometer'] = {
                'x': self.accelerometer.x,
                'y': self.accelerometer.y,
                'z': self.accelerometer.z
            }
        if self.gyroscope:
            result['gyroscope'] = {
                'x': self.gyroscope.x,
                'y': self.gyroscope.y,
                'z': self.gyroscope.z
            }
        if self.gps:
            result['gps'] = {
                'latitude': self.gps.latitude,
                'longitude': self.gps.longitude
            }
            if self.gps.altitude:
                result['gps']['altitude'] = self.gps.altitude
            if self.gps.accuracy:
                result['gps']['accuracy'] = self.gps.accuracy
        if self.barometer:
            result['barometer'] = self.barometer

        return result

    @staticmethod
    def from_dict(data: dict) -> 'SensorPayload':
        """Create from dictionary (e.g., from JSON)"""
        accelerometer = None
        if 'accelerometer' in data:
            acc = data['accelerometer']
            accelerometer = Accelerometer(x=acc['x'], y=acc['y'], z=acc['z'])

        gyroscope = None
        if 'gyroscope' in data:
            gyro = data['gyroscope']
            gyroscope = Gyroscope(x=gyro['x'], y=gyro['y'], z=gyro['z'])

        gps = None
        if 'gps' in data:
            gps_data = data['gps']
            gps = GPS(
                latitude=gps_data['latitude'],
                longitude=gps_data['longitude'],
                altitude=gps_data.get('altitude'),
                accuracy=gps_data.get('accuracy')
            )

        return SensorPayload(
            heart_rate=data['heartRate'],
            timestamp=data['timestamp'],
            accelerometer=accelerometer,
            gyroscope=gyroscope,
            gps=gps,
            barometer=data.get('barometer')
        )
