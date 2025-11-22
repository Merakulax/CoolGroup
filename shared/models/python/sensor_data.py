from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class Vector3:
    x: float
    y: float
    z: float

@dataclass
class Vector4:
    x: float
    y: float
    z: float
    w: float

@dataclass
class Location:
    latitude: float
    longitude: float
    accuracy: Optional[float] = None

@dataclass
class BloodPressure:
    systolic: int
    diastolic: int

@dataclass
class VitalsData:
    heartRate: Optional[int] = None
    restingHeartRate: Optional[int] = None
    hrvRMSSD: Optional[float] = None
    spo2: Optional[float] = None
    skinTemperature: Optional[float] = None
    bodyTemperature: Optional[float] = None
    bloodGlucose: Optional[float] = None
    bloodPressure: Optional[BloodPressure] = None
    vo2Max: Optional[float] = None
    ecgResult: Optional[str] = None

@dataclass
class BodyData:
    height: Optional[float] = None
    weight: Optional[float] = None
    bodyFat: Optional[float] = None
    bmi: Optional[float] = None

@dataclass
class ActivityData:
    stepCount: Optional[int] = None
    calories: Optional[int] = None
    activeHours: Optional[float] = None
    distance: Optional[float] = None
    speed: Optional[float] = None
    isIntensity: Optional[bool] = None

@dataclass
class RunningFormData:
    groundImpactAcceleration: Optional[float] = None
    verticalOscillation: Optional[float] = None
    groundContactTime: Optional[int] = None

@dataclass
class EnvironmentData:
    ambientLight: Optional[float] = None
    barometer: Optional[float] = None
    altitude: Optional[float] = None
    location: Optional[Location] = None

@dataclass
class MotionData:
    accelerometer: Optional[Vector3] = None
    gyroscope: Optional[Vector3] = None
    magnetometer: Optional[Vector3] = None
    gravity: Optional[Vector3] = None
    linearAcceleration: Optional[Vector3] = None
    rotationVector: Optional[Vector4] = None

@dataclass
class StatusData:
    wearDetection: Optional[Literal['WORN', 'NOT_WORN', 'UNKNOWN']] = None
    batteryLevel: Optional[int] = None

@dataclass
class WellbeingData:
    stressScore: Optional[int] = None
    emotionStatus: Optional[int] = None
    sleepScore: Optional[int] = None
    sleepStatus: Optional[str] = None

@dataclass
class SensorPayload:
    timestamp: int
    deviceId: Optional[str] = None
    vitals: Optional[VitalsData] = None
    body: Optional[BodyData] = None
    activity: Optional[ActivityData] = None
    runningForm: Optional[RunningFormData] = None
    environment: Optional[EnvironmentData] = None
    motion: Optional[MotionData] = None
    status: Optional[StatusData] = None
    wellbeing: Optional[WellbeingData] = None
