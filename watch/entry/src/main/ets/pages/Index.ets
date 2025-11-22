/**
 * Main Watch Face - Tamagotchi Pet Display
 * Entry point for the wearable application
 */
import { sensor } from '@kit.SensorServiceKit';
import { BusinessError } from '@kit.BasicServicesKit';
import PermissionsUtil from '../utils/PermissionsUtil';

@Entry
@Component
struct Index {
  @State accelerometer: string = '';
  @State gyroscope: string = '';
  @State light: string = '';
  @State pressure: string = '';
  @State humidity: string = '';
  @State temperature: string = '';
  @State orientation: string = '';
  @State gravity: string = '';
  @State heartData: number = 111;
  @State pedometer: number = 111;

  aboutToAppear(): void {
    const INTERVAL = 100_000_000; // 100 ms in nanoseconds

    PermissionsUtil.requestPermissions([
      'ohos.permission.ACCELEROMETER',
      'ohos.permission.ACTIVITY_MOTION',
      'ohos.permission.GYROSCOPE',
      'ohos.permission.READ_HEALTH_DATA'
    ]);

    try {
      sensor.on(sensor.SensorId.ACCELEROMETER, (data) => {
        this.accelerometer = `x:${data.x.toFixed(2)}, y:${data.y.toFixed(2)}, z:${data.z.toFixed(2)}`;
      }, { interval: INTERVAL });
    } catch (error) {
      let e: BusinessError = error as BusinessError;
      console.error(`Accelerometer error: ${e.message}`);
    }

    try {
      sensor.on(sensor.SensorId.PEDOMETER, (data: sensor.PedometerResponse) => {
        this.pedometer = data.steps;
        console.info('Succeeded in invoking once. Step count: ' + data.steps);
      });
    } catch (error) {
      let e: BusinessError = error as BusinessError;
      console.error(`Failed to invoke once. Code: ${e.code}, message: ${e.message}`);
    }

    try {
      sensor.on(sensor.SensorId.GYROSCOPE, (data) => {
        this.gyroscope = `x:${data.x.toFixed(2)}, y:${data.y.toFixed(2)}, z:${data.z.toFixed(2)}`;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error("Gyroscope failed.");
    }

    try {
      sensor.on(sensor.SensorId.GRAVITY, (data: sensor.GravityResponse) => {
        this.gravity = `x:${data.x.toFixed(2)}, y:${data.y.toFixed(2)}, z:${data.z.toFixed(2)}`;
        console.info('Gravity: x=' + data.x + ', y=' + data.y + ', z=' + data.z);
      }, { interval: INTERVAL });
      setTimeout(() => {
        sensor.off(sensor.SensorId.GRAVITY);
      }, 500);
    } catch (error) {
      let e: BusinessError = error as BusinessError;
      console.error(`Failed to invoke on. Code: ${e.code}, message: ${e.message}`);
    }

    try {
      sensor.on(sensor.SensorId.HEART_RATE, (data: sensor.HeartRateResponse) => {
        this.heartData = data.heartRate;
      }, { interval: INTERVAL });
      setTimeout(() => {
        sensor.off(sensor.SensorId.HEART_RATE);
      }, 500);
    } catch (error) {
      let e: BusinessError = error as BusinessError;
      console.error(`Failed to invoke on. Code: ${e.code}, message: ${e.message}`);
    }

    try {
      sensor.on(sensor.SensorId.AMBIENT_LIGHT, (data) => {
        this.light = `Light: ${data.intensity.toFixed(2)} lx`;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error("Light sensor failed.");
    }

    try {
      sensor.on(sensor.SensorId.BAROMETER, (data) => {
        this.pressure = `Pressure: ${data.pressure.toFixed(2)} hPa`;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error("Barometer failed.");
    }

    try {
      sensor.on(sensor.SensorId.HUMIDITY, (data) => {
        this.humidity = `Humidity: ${data.humidity.toFixed(2)}%`;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error("Humidity sensor failed.");
    }

    try {
      sensor.on(sensor.SensorId.AMBIENT_TEMPERATURE, (data) => {
        this.temperature = `Temp: ${data.temperature.toFixed(2)} °C`;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error("Temperature sensor failed.");
    }

    try {
      sensor.on(sensor.SensorId.ORIENTATION, (data) => {
        this.orientation = `Pitch: ${data.alpha.toFixed(2)}, Roll: ${data.beta.toFixed(2)}, Yaw: ${data.gamma.toFixed(2)}`;
      }, { interval: INTERVAL });
    } catch (error) {
      console.error("Orientation sensor failed.");
    }
  }

  aboutToDisappear(): void {
    sensor.off(sensor.SensorId.ACCELEROMETER);
    sensor.off(sensor.SensorId.GRAVITY);
    sensor.off(sensor.SensorId.GYROSCOPE);
    sensor.off(sensor.SensorId.AMBIENT_LIGHT);
    sensor.off(sensor.SensorId.BAROMETER);
    sensor.off(sensor.SensorId.HUMIDITY);
    sensor.off(sensor.SensorId.AMBIENT_TEMPERATURE);
    sensor.off(sensor.SensorId.ORIENTATION);
    sensor.off(sensor.SensorId.HEART_RATE);
  }

  build() {
    // post users     daten wie
    // name, pet name, age, health
    // this consists of the current time
    // the background image is fetched after posting the sensor data
    // there is also another page
  }
}