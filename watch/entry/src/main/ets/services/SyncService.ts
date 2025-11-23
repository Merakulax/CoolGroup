import { networkService } from '../utils/NetworkService';
import { PetState, SensorData } from '../models/types';

const SYNC_INTERVAL = 10000; // 10 seconds

class SyncService {
  private timerId: number | null = null;

  // The `start` method now accepts a `userId`.
  public start(
    updateCallback: (state: PetState) => void,
    getSensorData: () => SensorData,
    userId: string
  ): void {
    if (this.timerId !== null) {
      console.warn('SyncService is already running.');
      return;
    }

    console.log(`Starting SyncService for user: ${userId}`);

    // Run the loop immediately, then start the interval.
    this.syncLoop(updateCallback, getSensorData, userId);

    this.timerId = setInterval(() => {
      this.syncLoop(updateCallback, getSensorData, userId);
    }, SYNC_INTERVAL);
  }

  public stop(): void {
    if (this.timerId !== null) {
      clearInterval(this.timerId);
      this.timerId = null;
      console.log('SyncService stopped.');
    }
  }

  private async syncLoop(
    updateCallback: (state: PetState) => void,
    getSensorData: () => SensorData,
    userId: string
  ): Promise<void> {
    console.log('Executing sync loop with real data...');
    try {
      // 1. Get real sensor data via the provided getter function.
      const sensorData = getSensorData();
      await networkService.postSensorData(sensorData, userId);

      // 2. Retrieve the current pet state using the real userId.
      const petState = await networkService.getCurrentPetState(userId);

      // 3. Pass the new state back to the UI via the callback.
      if (petState) {
        updateCallback(petState);
      }

    } catch (error) {
      console.error('Error during sync loop:', JSON.stringify(error));
    }
  }
}

// Export a singleton instance of the service
export const syncService = new SyncService();
