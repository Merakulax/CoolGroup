/**
 * Main Watch Face - Tamagotchi Pet Display
 * Entry point for the wearable application
 */

@Entry
@Component
struct Index {
  @State petMood: string = 'Happy';
  @State heartRate: number = 0;
  @State currentTime: string = '';

  aboutToAppear() {
    // Initialize sensors
    this.initializeSensors();
    // Start time update
    this.updateTime();
  }

  initializeSensors() {
    // TODO: Initialize SensorService
    // Import from '../services/SensorService'
  }

  updateTime() {
    setInterval(() => {
      const now = new Date();
      this.currentTime = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
    }, 1000);
  }

  build() {
    Column() {
      // Time display
      Text(this.currentTime)
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
        .margin({ top: 20 })

      // Pet container
      Column() {
        // TODO: Implement pet animation based on petMood
        Text('🐾 Tamagotchi')
          .fontSize(48)
          .margin({ top: 40 })

        Text(this.petMood)
          .fontSize(16)
          .fontColor(Color.Gray)
      }
      .width('100%')
      .height('60%')
      .justifyContent(FlexAlign.Center)

      // Health metrics
      Row() {
        Text(`❤️ ${this.heartRate}`)
          .fontSize(18)
      }
      .margin({ top: 20 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#000000')
  }
}
