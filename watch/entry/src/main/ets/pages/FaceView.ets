
@Component
export struct FaceView {
  @Link imageUrl: string;
  @State private currentTime: string = "4:20";
  private timer: number = -1;

  aboutToAppear() {
    this.timer = setInterval(() => {
      const date = new Date();
      const hours = date.getHours();
      const minutes = date.getMinutes();
      this.currentTime = `${hours}:${minutes < 10 ? '0' + minutes : minutes}`;
    }, 1000);
  }

  aboutToDisappear() {
    if (this.timer !== -1) {
      clearInterval(this.timer);
      this.timer = -1;
    }
  }

  build() {
    Column() {
      Text(this.currentTime)
        .fontSize(50)
        .fontWeight(FontWeight.Bold)
        .margin({ top: 20 })
    }
    .justifyContent(FlexAlign.SpaceBetween)
    .width('100%')
    .height('100%')
    // Use the imageUrl from the parent, with a local placeholder as a fallback.
    .backgroundImage(this.imageUrl ? this.imageUrl : $r('app.media.background'))
    .backgroundImageSize(ImageSize.Cover)
  }
}
