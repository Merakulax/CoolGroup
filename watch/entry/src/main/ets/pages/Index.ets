import { sensor } from '@kit.SensorServiceKit';
import { abilityAccessCtrl, common, Permissions } from '@kit.AbilityKit';
import { networkService, TamagotchiState } from '../utils/NetworkService';
import HealthDataService from '../utils/HealthDataService';
import Log from '../utils/Log';

interface HeartRateResponse {
  heartRate?: number;
  value?: number;
}

@Entry
@Component
struct Index {
  @State heartRate: number = 0;
  @State stressScore: number = 0;
  @State sleepScore: number = 0;
  @State tamagotchiState: TamagotchiState = { image: '', text: 'Waiting for Tamagotchi...' };
  @State isTextExpanded: boolean = false;
  private context: common.UIAbilityContext | undefined = undefined;
  private atManager: abilityAccessCtrl.AtManager | null = null;

  aboutToAppear(): void {
    try {
      this.context = this.getUIContext().getHostContext() as common.UIAbilityContext;
    } catch (e) {
      this.context = undefined;
    }

    this.atManager = abilityAccessCtrl.createAtManager();
    this.requestPermissionsAndStart();
  }

  aboutToDisappear(): void {
    try {
      sensor.off(sensor.SensorId.HEART_RATE); // Keep existing sensor listener cleanup
      HealthDataService.unsubscribe(); // Unsubscribe HealthServiceKit listeners
    } catch (e) {
      Log.error('sensor.off or HealthDataService.unsubscribe failed', e.message)
    }
  }

  async requestPermissionsAndStart(): Promise<void> {
    const perms: Permissions[] = ['ohos.permission.READ_HEALTH_DATA', 'ohos.permission.INTERNET'];
    try {
      if (this.atManager && this.context) {
        const result = await this.atManager.requestPermissionsFromUser(this.context, perms);
        Log.info('permission request result: ' + JSON.stringify(result));
        this.startSensorListeners(); // Keep existing sensor listener for real-time HR
        this.startHealthDataListeners(); // Add HealthServiceKit listeners
      }
    } catch (err) {
      console.warn('permission request failed: ' + JSON.stringify(err));
    }
  }

  startSensorListeners(): void {
    try {
      // Existing Heart rate listener from SensorServiceKit
      sensor.on(sensor.SensorId.HEART_RATE, async (data: sensor.HeartRateResponse) => {
        const hr: number = (data as HeartRateResponse).heartRate ?? (data as HeartRateResponse).value ?? 0;
        if (typeof hr === 'number' && hr > 0) { // Only post valid heart rate
          this.heartRate = hr;
          Log.info(`SensorServiceKit heart rate -> ${hr}`);
          try {
            const stateUrl = await networkService.postHeartRate(hr);
            const newState = await networkService.getTamagotchiState(stateUrl);
            this.tamagotchiState = newState;
          } catch (e) {
            this.tamagotchiState = { image: '', text: `Error: ${e.message}` };
          }
        }
      });
    } catch (err) {
      console.error('startSensorListeners error: ' + JSON.stringify(err));
    }
  }

  startHealthDataListeners(): void {
    try {
      // Subscribe to HEART_RATE from HealthDataService (HealthServiceKit)
      HealthDataService.subscribeHeartRate((hr: number) => {
        this.heartRate = hr; // Update UI state with HealthServiceKit HR
        // The networkService.postHeartRate is already handled by the SensorServiceKit listener
        // If we want to replace SensorServiceKit with HealthServiceKit for posting, we would move it here.
        // For now, let's just update the UI with HealthServiceKit data as well if it comes through.
      });

      // Subscribe to STRESS from HealthDataService
      HealthDataService.subscribeStress((stress: number) => {
        this.stressScore = stress;
        Log.info(`HealthServiceKit stress score -> ${stress}`);
        // Optionally, integrate with networkService for stress data
      });

      // Subscribe to SLEEP_RECORD from HealthDataService
      HealthDataService.subscribeSleepRecord((sleep: number) => {
        this.sleepScore = sleep;
        Log.info(`HealthServiceKit sleep score -> ${sleep}`);
        // Optionally, integrate with networkService for sleep data
      });

    } catch (err) {
      Log.error('startHealthDataListeners error: ' + JSON.stringify(err));
    }
  }

  build() {
    Stack() {
      Image(this.tamagotchiState.image)
        .width('100%')
        .height('100%')
        .objectFit(ImageFit.Cover)

      Column() {
        Text(`Heart Rate: ${this.heartRate} bpm`)
          .fontSize(16)
          .fontColor(Color.White)
          .backgroundColor(0x000000, 0.5)
          .padding(5)
          .borderRadius(10)
          .margin({ bottom: 5 });

        Text(`Stress: ${this.stressScore}`)
          .fontSize(16)
          .fontColor(Color.White)
          .backgroundColor(0x000000, 0.5)
          .padding(5)
          .borderRadius(10)
          .margin({ bottom: 5 });

        Text(`Sleep Score: ${this.sleepScore}`)
          .fontSize(16)
          .fontColor(Color.White)
          .backgroundColor(0x000000, 0.5)
          .padding(5)
          .borderRadius(10)
          .margin({ bottom: 5 });

        Text(this.tamagotchiState.text)
          .fontSize(16)
          .fontColor(Color.White)
          .backgroundColor(0x000000, 0.5)
          .padding(10)
          .borderRadius(15)
          .width('90%')
          .maxLines(this.isTextExpanded ? 10 : 2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .onClick(() => {
            this.isTextExpanded = !this.isTextExpanded;
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.End)
      .padding({ bottom: 20 })
    }
    .width('100%')
    .height('100%')
  }
}