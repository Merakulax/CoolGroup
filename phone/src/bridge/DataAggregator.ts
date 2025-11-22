/**
 * DataAggregator - Batches high-frequency sensor data for cloud upload
 * Reduces network overhead by batching 50Hz streams into 1s chunks
 */

import { SensorPayload } from './WatchConnector';

export interface AggregatorStats {
  bufferSize: number;
  timeSinceLastUpload: number;
}

export class DataAggregator {
  private static readonly BATCH_SIZE = 50;  // 50 samples at 50Hz = 1 second
  private static readonly BATCH_INTERVAL_MS = 1000;  // 1 second max delay

  private buffer: SensorPayload[] = [];
  private lastUploadTime: number = Date.now();
  private uploadCallback?: (batch: SensorPayload[]) => void;

  /**
   * Append sensor reading to buffer
   * Triggers upload when batch size or time threshold reached
   */
  append(payload: SensorPayload): void {
    this.buffer.push(payload);

    const elapsedTime = Date.now() - this.lastUploadTime;
    if (this.buffer.length >= DataAggregator.BATCH_SIZE ||
        elapsedTime >= DataAggregator.BATCH_INTERVAL_MS) {
      this.uploadBatch();
    }
  }

  /**
   * Set callback for batch upload
   */
  onBatchReady(callback: (batch: SensorPayload[]) => void): void {
    this.uploadCallback = callback;
  }

  /**
   * Upload current batch to cloud
   */
  private uploadBatch(): void {
    if (this.buffer.length === 0) return;

    const batch = [...this.buffer];
    this.buffer = [];
    this.lastUploadTime = Date.now();

    console.log(`DataAggregator: Uploading batch of ${batch.length} samples`);
    this.uploadCallback?.(batch);
  }

  /**
   * Force immediate upload (e.g., when app goes to background)
   */
  flush(): void {
    this.uploadBatch();
  }

  /**
   * Get current buffer statistics
   */
  getStats(): AggregatorStats {
    return {
      bufferSize: this.buffer.length,
      timeSinceLastUpload: Date.now() - this.lastUploadTime
    };
  }
}
