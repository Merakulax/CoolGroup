import { sensor } from '@kit.SensorServiceKit';
import { BusinessError } from '@kit.BasicServicesKit';
import PermissionsUtil from '../utils/PermissionsUtil';
import { FaceView } from './FaceView';
import { MessageView } from './MessageView';
import { syncService } from '../services/SyncService';
import { networkService } from '../utils/NetworkService';
import { PetState, SensorData, Vector3, UserProfile } from '../models/types';

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
      // Instead of actually creating a User, use the user we created earlier
      // const userProfile: UserProfile = { name: "Hacker", pet_name: "Gemini" };
      // const newUser = await networkService.createUser(userProfile);
      const user: UserProfile = { name: "Hacker", pet_name: "Gemini"};
      this.userId = '7fe88792-63d1-4548-afc5-92c53e3436d3';

      // 2. If user is created, start the sync service
      if (this.userId) {
        this.petMessage = `Welcome, ${user.name}!`;
        syncService.start(
          // UI Update Callback
          (newState: PetState) => {
            this.petMessage = newState.message || '';
        this.petImageUrl = newState.image_url || ''; // Update the image URL
          },
          // Sensor Data Getter
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
      console.error(`App initialization failed: ${JSON.stringify(e)}`);
      this.petMessage = 'Error: Connection failed.';
    }
  }

  private subscribeToSensors(): void {
    const INTERVAL = 100_000_000; // 100 ms in nanoseconds

    PermissionsUtil.requestPermissions([
      'ohos.permission.ACCELEROMETER',
      'ohos.permission.ACTIVITY_MOTION',
      'ohos.permission.GYROSCOPE',
      'ohos.permission.READ_HEALTH_DATA'
    ]);

    try {
      sensor.on(sensor.SensorId.ACCELEROMETER, (data) => {
        this.accelData = { x: data.x, y: data.y, z: data.z };
        this.accelerometer = `x:${data.x.toFixed(2)}, y:${data.y.toFixed(2)}, z:${data.z.toFixed(2)}`;
      }, { interval: INTERVAL });
      sensor.on(sensor.SensorId.PEDOMETER, (data: sensor.PedometerResponse) => {
        this.pedometer = data.steps;
      });
      sensor.on(sensor.SensorId.GYROSCOPE, (data) => {
        this.gyroData = { x: data.x, y: data.y, z: data.z };
        this.gyroscope = `x:${data.x.toFixed(2)}, y:${data.y.toFixed(2)}, z:${data.z.toFixed(2)}`;
      }, { interval: INTERVAL });
      sensor.on(sensor.SensorId.HEART_RATE, (data: sensor.HeartRateResponse) => {
        this.heartData = data.heartRate;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error(`Sensor subscription failed: ${(error as BusinessError).message}`);
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