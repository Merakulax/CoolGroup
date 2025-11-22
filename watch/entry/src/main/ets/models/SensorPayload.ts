export interface Vitals {
  heartRate?: number;
  restingHeartRate?: number;
  hrvRMSSD?: number;
  spo2?: number;
  skinTemperature?: number;
  bodyTemperature?: number;
}

export interface Activity {
  stepCount?: number;
  calories?: number;
  distance?: number;
  speed?: number;
  isIntensity?: boolean;
}

export interface Motion {
  accelerometer?: { x: number; y: number; z: number; };
  gyroscope?: { x: number; y: number; z: number; };
  magnetometer?: { x: number; y: number; z: number; };
  gravity?: { x: number; y: number; z: number; };
  linearAcceleration?: { x: number; y: number; z: number; };
  rotationVector?: { x: number; y: number; z: number; w?: number; };
}

export interface Environment {
  ambientLight?: number;
  barometer?: number;
  altitude?: number;
}

export interface Status {
  wearDetection?: 'WORN' | 'NOT_WORN' | 'UNKNOWN';
  batteryLevel?: number;
}

export interface SensorPayload {
  timestamp: number;
  deviceId?: string;
  vitals?: Vitals;
  activity?: Activity;
  motion?: Motion;
  environment?: Environment;
  status?: Status;
}
