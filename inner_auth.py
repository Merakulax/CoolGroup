
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    creds = flow.run_console()
    
    print("\n--- CREDENTIALS START ---")
    print(json.dumps({
        'refresh_token': creds.refresh_token,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'token_uri': creds.token_uri
    }))
    print("--- CREDENTIALS END ---")

if __name__ == '__main__':
    main()
