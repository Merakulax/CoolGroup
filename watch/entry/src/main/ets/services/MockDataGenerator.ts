import { SensorData, Vector3 } from '../models/types';

// Defines the real-time data that will be passed into the generator
export interface RealtimeData {
  heartRate: number;
  accel: Vector3;
  gyro: Vector3;
  steps: number;
}

class MockDataGenerator {

  /**
   * Generates a complete sensor data payload by combining real-time sensor
   * readings with mocked data that tells a consistent story.
   * 
   * The story: A previously healthy user who has not slept for 2 days during a hackathon.
   */
  public generateFullPayload(realtime: RealtimeData): SensorData {

    const payload: SensorData = {
      timestamp: Date.now(),
      deviceId: 'mock_watch_id_123',

      vitals: {
        heartRate: realtime.heartRate, // Real data
        restingHeartRate: 75, // Mocked: Elevated due to stress/no sleep
        hrvRMSSD: 18,         // Mocked: Very low, indicating high fatigue
        spo2: 96,             // Mocked: Plausible
        skinTemperature: 34.5, // Mocked: Plausible
        bodyTemperature: 37.1, // Mocked: Plausible
      },

      activity: {
        stepCount: realtime.steps, // Real data
        calories: 2200 + (realtime.steps * 0.04), // Mocked: High base calories for an active person
        distance: realtime.steps * 0.762, // Mocked: Simple estimation
        speed: 1.1, // Mocked: Average walking speed
        isIntensity: (realtime.heartRate > 120), // Mocked: Simple intensity check
      },

      runningForm: {
        // Mocked: Plausible data for a runner
        groundImpactAcceleration: 1.5,
        verticalOscillation: 8.2,
        groundContactTime: 250,
      },

      environment: {
        // Mocked: Typical indoor environment
        ambientLight: 300,
        barometer: 1013.25,
        altitude: 120,
      },

      motion: {
        accelerometer: realtime.accel, // Real data
        gyroscope: realtime.gyro,       // Real data
        // Mocked: Zeroed out as they are less critical for this scenario
        magnetometer: { x: 0, y: 0, z: 0 },
        gravity: { x: 0, y: 0, z: -9.8 },
        linearAcceleration: { x: 0, y: 0, z: 0 },
        rotationVector: { x: 0, y: 0, z: 0, w: 1 },
      },

      status: {
        wearDetection: 'WORN',
        batteryLevel: 65, // Mocked
      },

      wellbeing: {
        // This section directly reflects the story
        sleepScore: 15,   // Mocked: Very low due to no sleep
        stressScore: 85,  // Mocked: High due to hackathon
        emotionStatus: 1, // Mocked: Unpleasant
      }
    };

    return payload;
  }
}

export const mockDataGenerator = new MockDataGenerator();
