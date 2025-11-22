import http from '@ohos.net.http';

export interface TamagotchiState {
  image: string;
  text: string;
}

class NetworkService {
  public async getFromGoogle(): Promise<string> {
    console.log('Fetching from Google...');

    const httpRequest = http.createHttp();

    try {
      const response = await httpRequest.request(
        'https://www.google.com',
        {
          method: http.RequestMethod.GET
        }
      );

      if (response.responseCode === http.ResponseCode.OK) {
        return response.result as string;
      } else {
        console.error(`HTTP Error: ${response.responseCode} - ${response.result}`);
        throw new Error(`Server responded with code: ${response.responseCode}`);
      }
    } catch (error) {
      console.error('Failed to fetch from Google:', error);
      throw error;
    } finally {
      httpRequest.destroy();
    }
  }

  public async getTamagotchiState(url: string): Promise<TamagotchiState> {
    console.log(`Fetching Tamagotchi state from: ${url}`);

    const httpRequest = http.createHttp();

    try {
      const response = await httpRequest.request(url, { method: http.RequestMethod.GET });

      if (response.responseCode === http.ResponseCode.OK) {
        return JSON.parse(response.result as string);
      } else {
        console.error(`HTTP Error: ${response.responseCode} - ${response.result}`);
        throw new Error(`Server responded with code: ${response.responseCode}`);
      }
    } catch (error) {
      console.error('Failed to fetch Tamagotchi state:', error);
      throw error;
    } finally {
      httpRequest.destroy();
    }
  }
  public async postHeartRate(heartRate: number): Promise<string> {
    console.log(`Posting heart rate: ${heartRate}`);

    const httpRequest = http.createHttp();
    const url = 'https://lnt6x6tek2.execute-api.eu-central-1.amazonaws.com/echo'; // Replace with your actual server URL

    const payload = {
      heartRate: heartRate,
      timestamp: Date.now()
    };

    try {
      const response = await httpRequest.request(
        url,
        {
          method: http.RequestMethod.POST,
          header: {
            'Content-Type': 'application/json'
          },
          extraData: JSON.stringify(payload)
        }
      );

      if (response.responseCode === http.ResponseCode.OK) {
        return response.result as string;
      } else {
        console.error(`HTTP Error: ${response.responseCode} - ${response.result}`);
        throw new Error(`Server responded with code: ${response.responseCode}`);
      }
    } catch (error) {
      console.error('Failed to post heart rate:', error);
      throw error;
    } finally {
      httpRequest.destroy();
    }
  }
}

export const networkService = new NetworkService();
