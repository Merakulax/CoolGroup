import type { BusinessError } from '@ohos.base';

@Component
export struct HealthStatsView {
  @Link heartRate: number;
  @Link totalSteps: number;

  build() {
    Column({ space: 15 }) {
      // Heart Rate
      Row({ space: 10 }) {
        Text('❤️').fontSize(28)
        Text('Heart Rate')
          .fontSize(20)
      }.alignItems(VerticalAlign.Center)

      Text(`${this.heartRate > 0 ? this.heartRate : '--'} bpm`)
        .fontSize(38)
        .fontWeight(FontWeight.Lighter)

      Divider().strokeWidth(1).color(Color.Gray)

      // Steps
      Row({ space: 10 }) {
        Text('👟').fontSize(28)
        Text('Steps')
          .fontSize(20)
      }.alignItems(VerticalAlign.Center)

      Text(`${this.totalSteps}`)
        .fontSize(38)
        .fontWeight(FontWeight.Lighter)

    }
    .padding(20)
    .width('100%')
    .height('100%')
    .backgroundColor(Color.Black);
  }
}

