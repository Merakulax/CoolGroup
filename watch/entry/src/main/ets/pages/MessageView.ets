
@Component
export struct MessageView {
  @Link message: string;

  build() {
    Scroll() {
      Column() {
        Text(this.message)
          .textAlign(TextAlign.Center)
          .fontSize('18fp')
      }
      .width('75%') // Make the text area wider
      .padding({ top: '25%', bottom: '25%' }) // Add vertical padding to center the content
    }
    .width('100%')
    .height('100%')
    .scrollable(ScrollDirection.Vertical)
    .align(Alignment.Center) // Keep the column centered
  }
}
