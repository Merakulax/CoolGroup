import { sensor } from '@kit.SensorServiceKit';
import { BusinessError } from '@kit.BasicServicesKit';
import abilityAccessCtrl from '@ohos.abilityAccessCtrl';
import type { Permissions } from '@ohos.abilityAccessCtrl';
import { FaceView } from './FaceView';
import { MessageView } from './MessageView';
import { HealthStatsView } from '../views/HealthStatsView';
import { networkService } from '../utils/NetworkService';
import { syncService } from '../services/SyncService';
import { mockDataGenerator, RealtimeData } from '../services/MockDataGenerator';
import { PetState, SensorData, Vector3, UserProfile, User} from '../models/types';

@Entry
@Component
struct Index {
  // Sensor data for display
  @State accelerometer: string = '';
  @State gyroscope: string = '';
  @State heartData: number = 0;
  @State totalSteps: number = 0;

  // Raw sensor data for backend
  @State accelData: Vector3 = { x: 0, y: 0, z: 0 };
  @State gyroData: Vector3 = { x: 0, y: 0, z: 0 };

  // App and User state
  @State userId: string | null = null;
  @State petMessage: string = 'Initializing...';
  @State petVideoUrl: string = '';

  aboutToAppear(): void {
    this.initializeApp();
  }

  async initializeApp(): Promise<void> {
    try {
      // 0. Request permissions before starting sensors
      const permissionGranted = await this.requestPermissions();
      if (permissionGranted) {
        this.subscribeToSensors();
      } else {
        this.petMessage = 'Sensor permissions denied. Key features will not work.';
      }

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
            this.petVideoUrl = newState.video_url || '';
          },
          // Sensor Data Getter
          (): SensorData => {
            const realtimeData: RealtimeData = {
              heartRate: this.heartData,
              accel: this.accelData,
              gyro: this.gyroData,
              steps: this.totalSteps
            };
            return mockDataGenerator.generateFullPayload(realtimeData);
          },
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

    try {
      sensor.on(sensor.SensorId.HEART_RATE, (data: sensor.HeartRateResponse) => {
        this.heartData = data.heartRate;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error(`Heart Rate subscription failed: ${(error as BusinessError).message}`);
    }

    try {
      sensor.on(sensor.SensorId.PEDOMETER, (data: sensor.PedometerResponse) => {
        console.info(`Received Pedometer: ${data.steps}`);
        this.totalSteps = data.steps;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error(`Pedometer subscription failed: ${(error as BusinessError).message}`);
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
      FaceView({ videoUrl: this.petVideoUrl })
      MessageView({ message: this.petMessage })
      HealthStatsView({ heartRate: $heartData, totalSteps: $totalSteps })
    }
    .indicator(true)
    .vertical(false)
    .loop(true)
  }

  async requestPermissions(): Promise<boolean> {
    let atManager = abilityAccessCtrl.createAtManager();
    try {
      const context = getContext(this);
      const permissions: Array<Permissions> = [
        'ohos.permission.ACTIVITY_MOTION',
        'ohos.permission.READ_HEALTH_DATA',
        'ohos.permission.ACCELEROMETER',
        'ohos.permission.GYROSCOPE'
      ];
      const result = await atManager.requestPermissionsFromUser(context, permissions);
      if (result && result.authResults[0] === 0 && result.authResults[1] === 0) {
        console.info('[Index] All required permissions granted.');
        return true;
      } else {
        console.error('[Index] One or more permissions were denied.');
        return false;
      }
    } catch (err) {
      console.error(`[Index] Failed to request permissions: ${JSON.stringify(err)}`);
      return false;
    }
  }
}