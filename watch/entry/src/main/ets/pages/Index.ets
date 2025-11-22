import { sensor } from '@kit.SensorServiceKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { FaceView } from './FaceView';
import { MessageView } from './MessageView';
import { syncService } from '../services/SyncService';
import { networkService } from '../utils/NetworkService';
import { PetState, SensorData, Vector3, UserProfile, User, Motion } from '../models/types';

@Entry
@Component
struct Index {
  // Sensor data for display
  @State accelerometer: string = '';
  @State gyroscope: string = '';
  @State heartData: number = 0;
  @State pedometer: number = 0;

  // Raw sensor data for backend
  @State accelData: Vector3 = { x: 0, y: 0, z: 0 };
  @State gyroData: Vector3 = { x: 0, y: 0, z: 0 };

  // App and User state
  @State userId: string | null = null;
  @State petMessage: string = 'Initializing...';
  @State petImageUrl: string = '';

  aboutToAppear(): void {
    this.subscribeToSensors();
    this.initializeApp();
  }

  async initializeApp(): Promise<void> {
    try {
      this.petMessage = 'Creating user...';
      // 1. Create user with a hardcoded profile for this MVP
      const userProfile: UserProfile = { name: "Hacker", pet_name: "Gemini" };
      const newUser: User = await networkService.createUser(userProfile);
      this.userId = newUser.user_id;

      // 2. If user is created, start the sync service
      if (this.userId) {
        this.petMessage = `Welcome, ${newUser.name}!`;
        syncService.start(
          // UI Update Callback
          (newState: PetState) => {
            this.petMessage = newState.message || '';
            this.petImageUrl = newState.image_url || '';
          },
          // Sensor Data Getter - Simplified to always send data
          (): SensorData => ({
            timestamp: Date.now(),
            vitals: { heartRate: this.heartData },
            motion: { accelerometer: this.accelData, gyroscope: this.gyroData }
          }),
          // Real User ID
          this.userId
        );
      } else {
        this.petMessage = 'Error: Could not create user.';
      }
    } catch (e) {
      const error = e as BusinessError;
      console.error(`App initialization failed: ${error.code}, ${error.message}`);
      this.petMessage = 'Error: Connection failed.';
    }
  }

  private subscribeToSensors(): void {
    const INTERVAL = 100_000_000; // 100 ms in nanoseconds

    // Subscribe to sensors using the simple, correct pattern.
    try {
      sensor.on(sensor.SensorId.HEART_RATE, (data: sensor.HeartRateResponse) => {
        console.info(`[Sensor] Heart Rate data received: ${JSON.stringify(data)}`);
        this.heartData = data.heartRate;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error(`Heart Rate subscription failed: ${(error as BusinessError).message}`);
    }

    try {
      sensor.on(sensor.SensorId.ACCELEROMETER, (data: sensor.AccelerometerResponse) => {
        this.accelData = { x: data.x, y: data.y, z: data.z };
        this.accelerometer = `x:${data.x.toFixed(2)}, y:${data.y.toFixed(2)}, z:${data.z.toFixed(2)}`;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error(`Accelerometer subscription failed: ${(error as BusinessError).message}`);
    }

    try {
      sensor.on(sensor.SensorId.PEDOMETER, (data: sensor.PedometerResponse) => {
        this.pedometer = data.steps;
      });
    } catch (error) {
      console.error(`Pedometer subscription failed: ${(error as BusinessError).message}`);
    }

    try {
      sensor.on(sensor.SensorId.GYROSCOPE, (data: sensor.GyroscopeResponse) => {
        this.gyroData = { x: data.x, y: data.y, z: data.z };
        this.gyroscope = `x:${data.x.toFixed(2)}, y:${data.y.toFixed(2)}, z:${data.z.toFixed(2)}`;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error(`Gyroscope subscription failed: ${(error as BusinessError).message}`);
    }
  }

  aboutToDisappear(): void {
    syncService.stop();
    this.unsubscribeFromSensors();
  }

  private unsubscribeFromSensors(): void {
    sensor.off(sensor.SensorId.ACCELEROMETER);
    sensor.off(sensor.SensorId.GYROSCOPE);
    sensor.off(sensor.SensorId.HEART_RATE);
    sensor.off(sensor.SensorId.PEDOMETER);
  }

  build() {
    Swiper() {
      FaceView({ imageUrl: this.petImageUrl })
      MessageView({ message: this.petMessage })
    }
    .indicator(true)
    .vertical(false)
    .loop(true)
  }
}