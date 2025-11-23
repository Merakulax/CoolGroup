import http from '@ohos.net.http';
import { BusinessError } from '@kit.BasicServicesKit';
import Log from './Log';
import { SensorData, PetState, User, UserProfile } from '../models/types';

const BASEURL = 'https://lnt6x6tek2.execute-api.eu-central-1.amazonaws.com/api/v1';

class NetworkService {

  public async createUser(profile: UserProfile): Promise<User> {
    const url = `${BASEURL}/users`;
    Log.info(`[NetworkService] Creating user. URL: ${url}, Payload: ${JSON.stringify(profile)}`);
    const httpRequest = http.createHttp();
    try {
      const response = await httpRequest.request(url, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify(profile)
      });

      if (response.responseCode === 201) { // 201 Created
        Log.info(`[NetworkService] User created (201). Response: ${response.result}`);
        return JSON.parse(response.result as string) as User;
      } else {
        Log.error(`[NetworkService] Failed to create user. Status: ${response.responseCode}, Data: ${response.result}`);
        throw new Error(`Server responded with status: ${response.responseCode}`);
      }
    } catch (err) {
      const businessError = err as BusinessError;
      Log.error(`[NetworkService] Create user error: Code: ${businessError.code}, message: ${businessError.message}`);
      throw err;
    } finally {
      httpRequest.destroy();
    }
  }

  public async getCurrentPetState(userId: string): Promise<PetState> {
    const url = `${BASEURL}/user/${userId}/state`;
    Log.info(`[NetworkService] Getting pet state. URL: ${url}`);
    const httpRequest = http.createHttp();
    try {
      const response = await httpRequest.request(url, { method: http.RequestMethod.GET });
      if (response.responseCode === 200) {
        Log.info(`[NetworkService] Get pet state (200). Response: ${response.result}`);
        return JSON.parse(response.result as string) as PetState;
      } else {
        Log.error(`[NetworkService] Failed to get pet state. Status: ${response.responseCode}, Data: ${response.result}`);
        throw new Error(`Server responded with status: ${response.responseCode}`);
      }
    } catch (err) {
      const businessError = err as BusinessError;
      Log.error(`[NetworkService] Get pet state error: Code: ${businessError.code}, message: ${businessError.message}`);
      throw err;
    } finally {
      httpRequest.destroy();
    }
  }

  public async postSensorData(payload: SensorData, userId: string): Promise<void> {
    const url = `${BASEURL}/user/${userId}/data`;
    // Construct the correct request body that the server expects
    const requestBody = {
      user_id: userId,
      batch: [payload] // The API expects the data within a 'batch' array
    };
    Log.info(`[NetworkService] Posting sensor data. URL: ${url}, Payload: ${JSON.stringify(requestBody)}`);
    const httpRequest = http.createHttp();
    try {
      const response = await httpRequest.request(url, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify(requestBody)
      });
      if (response.responseCode === 202 || response.responseCode === 200) { // 202 Accepted or 200 OK
        Log.info(`[NetworkService] Post sensor data accepted (202).`);
      } else {
        Log.error(`[NetworkService] Post sensor data failed. Status: ${response.responseCode}, Data: ${response.result}`);
        throw new Error(`Server responded with status: ${response.responseCode}`);
      }
    } catch (err) {
      const businessError = err as BusinessError;
      Log.error(`[NetworkService] Post sensor data error: Code: ${businessError.code}, message: ${businessError.message}`);
      throw err;
    } finally {
      httpRequest.destroy();
    }
  }
}

export const networkService = new NetworkService();
