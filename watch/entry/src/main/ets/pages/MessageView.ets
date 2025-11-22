
@Component
export struct MessageView {
  @Link message: string;

  build() {
    Scroll() {
      Column() {
        Text(this.message)
          .padding(10)
      }
      .width('100%')
      .justifyContent(FlexAlign.Center)
    }
    .width('100%')
    .height('100%')
  }
}
