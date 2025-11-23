// 131.159.195.211:35809

@Component
export struct HealthStatsView {
  @Link heartRate: number;

  build() {
    Row({ space: 15 }) {
      Text('❤️').fontSize(28)
        .fontSize(20)
      Text(`${this.heartRate > 0 ? this.heartRate : '--'} bpm`)
        .fontSize(38)
        .fontWeight(FontWeight.Lighter)
    }
    .justifyContent(FlexAlign.Center)
    .padding(20)
    .width('100%')
    .height('100%')
    .backgroundColor(Color.Black);
  }
}

