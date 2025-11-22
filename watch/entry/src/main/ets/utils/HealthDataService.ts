import { healthStore } from '@kit.HealthServiceKit';
import Logger from './Log'; // Assuming Log.ts provides a default export for logging

const TAG = 'HealthDataService';

class HealthDataService {
  private healthStoreObserver: healthStore.HealthStoreObserver | null = null;

  constructor() {
    Logger.info(TAG, 'HealthDataService initialized.');
  }

  // Subscribe to HEART_RATE data
  subscribeHeartRate(callback: (heartRate: number) => void): void {
    const dataType = healthStore.healthDataTypes.HEART_RATE;
    const observerOptions: healthStore.HealthStoreObserverOptions = {
      dataType: dataType,
      // You might need to specify a time range or other options depending on how you want to receive data.
      // For real-time, continuous observation, options might be minimal or default to recent data.
    };

    if (!this.healthStoreObserver) {
      this.healthStoreObserver = healthStore.createHealthStoreObserver(observerOptions);
    }

    this.healthStoreObserver.on('change', (dataChangeInfo: healthStore.DataChangeInfo) => {
      if (dataChangeInfo.dataType === dataType) {
        // Here, you would query the latest heart rate data using healthStore.queryHealthData
        // For now, let's just log a placeholder or mock data for demonstration
        const mockHeartRate = Math.floor(Math.random() * (120 - 60 + 1)) + 60; // Mock HR between 60-120
        Logger.info(TAG, `Received HEART_RATE data: ${mockHeartRate} bpm`);
        callback(mockHeartRate);
      }
    });

    Logger.info(TAG, `Subscribed to ${dataType.name} changes.`);
  }

  // TODO: Implement subscribeStress and subscribeSleepRecord
  subscribeStress(callback: (stressScore: number) => void): void {
    const dataType = healthStore.healthDataTypes.STRESS;
    const observerOptions: healthStore.HealthStoreObserverOptions = {
      dataType: dataType,
    };

    // Need to handle creation of observer if not already done, or add another one
    // For simplicity, let's assume one observer for all for now, but in reality, might need multiple.
    // Or a more generic approach with the existing observer.
    if (!this.healthStoreObserver) {
        this.healthStoreObserver = healthStore.createHealthStoreObserver(observerOptions);
    }
    
    this.healthStoreObserver.on('change', (dataChangeInfo: healthStore.DataChangeInfo) => {
        if (dataChangeInfo.dataType === dataType) {
            const mockStress = Math.floor(Math.random() * (99 - 1 + 1)) + 1; // Mock Stress between 1-99
            Logger.info(TAG, `Received STRESS data: ${mockStress} score`);
            callback(mockStress);
        }
    });
    Logger.info(TAG, `Subscribed to ${dataType.name} changes.`);
  }

  subscribeSleepRecord(callback: (sleepScore: number) => void): void {
    const dataType = healthStore.healthDataTypes.SLEEP_RECORD;
    const observerOptions: healthStore.HealthStoreObserverOptions = {
      dataType: dataType,
    };

    if (!this.healthStoreObserver) {
        this.healthStoreObserver = healthStore.createHealthStoreObserver(observerOptions);
    }
    
    this.healthStoreObserver.on('change', (dataChangeInfo: healthStore.DataChangeInfo) => {
        if (dataChangeInfo.dataType === dataType) {
            const mockSleepScore = Math.floor(Math.random() * (100 - 0 + 1)) + 0; // Mock Sleep Score between 0-100
            Logger.info(TAG, `Received SLEEP_RECORD data: ${mockSleepScore} score`);
            callback(mockSleepScore);
        }
    });
    Logger.info(TAG, `Subscribed to ${dataType.name} changes.`);
  }

  unsubscribe(): void {
    if (this.healthStoreObserver) {
      this.healthStoreObserver.off('change');
      healthStore.destroyHealthStoreObserver(this.healthStoreObserver);
      this.healthStoreObserver = null;
      Logger.info(TAG, 'Unsubscribed from HealthStore changes.');
    }
  }
}

export default new HealthDataService();