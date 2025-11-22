/**
 * Sensor Data Definitions
 * Matches shared/contracts/sensor_data.json v2.0.0
 */

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface Vector4 {
  x: number;
  y: number;
  z: number;
  w: number;
}

export interface Location {
  latitude: number;
  longitude: number;
  accuracy?: number;
}

export interface BloodPressure {
  systolic: number;
  diastolic: number;
}

export interface VitalsData {
  heartRate?: number;
  restingHeartRate?: number;
  hrvRMSSD?: number;
  spo2?: number;
  skinTemperature?: number;
  bodyTemperature?: number;
  bloodGlucose?: number; // mmol/L
  bloodPressure?: BloodPressure;
  vo2Max?: number; // ml/kg/min
  ecgResult?: string;
}

export interface BodyData {
  height?: number; // meters
  weight?: number; // kg
  bodyFat?: number; // %
  bmi?: number;
}

export interface ActivityData {
  stepCount?: number;
  calories?: number;
  activeHours?: number;
  distance?: number;
  speed?: number;
  isIntensity?: boolean;
}

export interface RunningFormData {
  groundImpactAcceleration?: number;
  verticalOscillation?: number;
  groundContactTime?: number;
}

export interface EnvironmentData {
  ambientLight?: number; // lux
  barometer?: number; // hPa
  altitude?: number; // meters
  location?: Location;
}

export interface MotionData {
  accelerometer?: Vector3;
  gyroscope?: Vector3;
  magnetometer?: Vector3;
  gravity?: Vector3;
  linearAcceleration?: Vector3;
  rotationVector?: Vector4;
}

export interface StatusData {
  wearDetection?: 'WORN' | 'NOT_WORN' | 'UNKNOWN';
  batteryLevel?: number;
}

export interface WellbeingData {
  stressScore?: number;
  emotionStatus?: number; // 1: Unpleasant, 2: Neutral, 3: Pleasant
  sleepScore?: number;
  sleepStatus?: string;
}

export interface SensorPayload {
  timestamp: number;
  deviceId?: string;
  vitals?: VitalsData;
  body?: BodyData;
  activity?: ActivityData;
  runningForm?: RunningFormData;
  environment?: EnvironmentData;
  motion?: MotionData;
  status?: StatusData;
  wellbeing?: WellbeingData;
}
