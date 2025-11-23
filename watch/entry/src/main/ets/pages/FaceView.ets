
@Component
export struct FaceView {
  @Link videoUrl: string;
  @State private currentTime: string = "4:20";
  private timer: number = -1;
  private videoController: VideoController = new VideoController();

  aboutToAppear() {
    this.timer = setInterval(() => {
      const date = new Date();
      const hours = date.getHours();
      const minutes = date.getMinutes();
      this.currentTime = `${hours}:${minutes < 10 ? '0' + minutes : minutes}`;
    }, 1000);
    this.videoController.start();
  }

  aboutToDisappear() {
    if (this.timer !== -1) {
      clearInterval(this.timer);
      this.timer = -1;
    }
    this.videoController.stop();
  }

  build() {
    Stack() {
      Video({ src: this.videoUrl, controller: this.videoController })
        .width('100%')
        .height('100%')
        .autoPlay(true)
        .loop(true)
        .controls(false)
        .objectFit(ImageFit.Cover)

      Column() {
        Text(this.currentTime)
          .fontSize(50)
          .fontWeight(FontWeight.Bold)
          .margin({ top: 20 })
      }
      .justifyContent(FlexAlign.SpaceBetween)
      .width('100%')
      .height('100%')
    }
  }
}
