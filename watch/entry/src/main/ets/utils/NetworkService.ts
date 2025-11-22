import { rcp } from '@kit.RemoteCommunicationKit';
import { BusinessError } from '@kit.BasicServicesKit';
import Log from './Log';
import { SensorPayload } from '../models/SensorPayload';

export interface TamagotchiState {
  image_url: string;
  message: string;
}

class NetworkService {

  public async postSensorData(payload: SensorPayload): Promise<TamagotchiState> {
    Log.info('Posting sensor data...');

    const session = rcp.createSession();
    // The user's URL needs to be updated to point to the new endpoint
    const postURL = 'https://lnt6x6tek2.execute-api.eu-central-1.amazonaws.com/sensor-data';

    const postContent: rcp.RequestContent = {
      // rcp.RequestContent fields must be strings, so we stringify the whole payload
      fields: { 'payload': JSON.stringify(payload) }
    };

    try {
      const response = await session.post(postURL, postContent);
      if (response.statusCode === 200) { // Assuming 200 OK for success
        return JSON.parse(response.toString());
      } else {
        throw new Error(`Server responded with status: ${response.statusCode}, data: ${response.toString()}`);
      }
    } catch (err) {
      const businessError = err as BusinessError;
      Log.error(`Response err: Code is ${JSON.stringify(businessError.code)}, message is ${JSON.stringify(businessError.message)}`);
      throw new Error(`Failed to post sensor data: ${businessError.message}`);
    } finally {
      // rcp session does not have a destroy method
    }
  }
}

export const networkService = new NetworkService();
