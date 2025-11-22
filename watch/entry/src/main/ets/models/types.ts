// --- Pet State ---
// Based on shared/contracts/pet_state.json

export interface PetState {
  stateIndex: number;
  mood: 'Happy' | 'Energetic' | 'Sleepy' | 'Concerned' | 'Anxious' | 'Recovering' | 'Proud';
  energy: number;
  message?: string;
  image_url?: string;
  // For the purpose of this feature, we only need the message.
  // Other fields from the contract can be added here as needed.
  timestamp: number;
}


// --- Sensor Data ---
// Based on shared/contracts/sensor_data.json
// A simplified version for what the watch client might send.

export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface Vitals {
  heartRate?: number;
  hrvRMSSD?: number;
  spo2?: number;
}

export interface Motion {
  accelerometer?: Vector3;
  gyroscope?: Vector3;
}

export interface SensorData {
  timestamp: number;
  deviceId?: string;
  vitals?: Vitals;
  motion?: Motion;
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
