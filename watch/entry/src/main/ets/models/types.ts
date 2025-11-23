// --- Pet State ---
// Based on shared/contracts/pet_state.json

export interface PetState {
  stateIndex: number;
  mood: 'Happy' | 'Energetic' | 'Sleepy' | 'Concerned' | 'Anxious' | 'Recovering' | 'Proud';
  energy: number;
  message?: string;
  image_url?: string;
  timestamp: number;
}

// --- Sensor Data Payload (Complete) ---
// Based on shared/contracts/sensor_data.json

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface Vector4 extends Vector3 {
  w: number;
}

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

export interface RunningForm {
  groundImpactAcceleration?: number;
  verticalOscillation?: number;
  groundContactTime?: number;
}

export interface Location {
  latitude?: number;
  longitude?: number;
  accuracy?: number;
}

export interface Environment {
  ambientLight?: number;
  barometer?: number;
  altitude?: number;
  location?: Location;
}

export interface Motion {
  accelerometer?: Vector3;
  gyroscope?: Vector3;
  magnetometer?: Vector3;
  gravity?: Vector3;
  linearAcceleration?: Vector3;
  rotationVector?: Vector4;
}

export interface Status {
  wearDetection?: 'WORN' | 'NOT_WORN' | 'UNKNOWN';
  batteryLevel?: number;
}

export interface Wellbeing {
  stressScore?: number;
  emotionStatus?: number; // 1: Unpleasant, 2: Neutral, 3: Pleasant
  sleepScore?: number;
}

export interface SensorData {
  timestamp: number;
  deviceId?: string;
  vitals?: Vitals;
  activity?: Activity;
  runningForm?: RunningForm;
  environment?: Environment;
  motion?: Motion;
  status?: Status;
  wellbeing?: Wellbeing;
}

// --- User Profile ---
// Based on shared/contracts/user_profile.json

/**
 * Data sent TO the backend to create a user.
 */
export interface UserProfile {
  name: string;
  pet_name: string;
  age?: number;
  health_goals?: string[];
}

/**
 * Data received FROM the backend after user creation.
 */
export interface User {
  user_id: string;
  name: string;
  pet_name: string;
  age?: number;
  health_goals?: string[];
  avatar_url?: string;
}
