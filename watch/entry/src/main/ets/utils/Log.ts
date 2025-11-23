class Log {
  static info(tagOrMessage: string, message?: string): void {
    if (message) {
      console.info(`${tagOrMessage}: ${message}`);
    } else {
      console.info(tagOrMessage);
    }
  }

  static error(tagOrMessage: string, message?: string): void {
    if (message) {
      console.error(`${tagOrMessage}: ${message}`);
    } else {
      console.error(tagOrMessage);
    }
  }

  static warn(tagOrMessage: string, message?: string): void {
    if (message) {
      console.warn(`${tagOrMessage}: ${message}`);
    } else {
      console.warn(tagOrMessage);
    }
  }
}

export default Log;