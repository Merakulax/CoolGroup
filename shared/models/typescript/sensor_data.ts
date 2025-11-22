/**
 * Sensor Data Models - TypeScript/ArkTS
 * Auto-generated from contracts/sensor_data.json
 */

export interface Accelerometer {
  x: number;
  y: number;
  z: number;
}

export interface Gyroscope {
  x: number;
  y: number;
  z: number;
}

export interface GPS {
  latitude: number;
  longitude: number;
  altitude?: number;
  accuracy?: number;
}

/**
 * Sensor data payload from Watch to Phone/Cloud
 */
export interface SensorPayload {
  heartRate: number;
  timestamp: number;
  accelerometer?: Accelerometer;
  gyroscope?: Gyroscope;
  gps?: GPS;
  barometer?: number;
}

/**
 * Validate sensor payload against schema
 */
export function validateSensorPayload(payload: any): payload is SensorPayload {
  if (typeof payload.heartRate !== 'number' || payload.heartRate < 30 || payload.heartRate > 220) {
    return false;
  }
  if (typeof payload.timestamp !== 'number') {
    return false;
  }
  return true;
}
