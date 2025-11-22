import os
import sys
import subprocess
import json

VENV_DIR = ".auth_venv"

def create_venv():
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    
    pip_exe = os.path.join(VENV_DIR, "bin", "pip")
    print("Installing dependencies...")
    subprocess.check_call([pip_exe, "install", "google-auth-oauthlib"])

def run_auth():
    python_exe = os.path.join(VENV_DIR, "bin", "python")
    
    script = r'''
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES)
    
    # Use OOB (Out of Band) flow for manual copy-paste
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print(f"\nPlease visit this URL to authorize:\n{auth_url}\n")
    
    code = input("Enter the authorization code: ")
    
    flow.fetch_token(code=code)
    creds = flow.credentials
    
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
'''
    with open("inner_auth.py", "w") as f:
        f.write(script)
        
    print("Starting authentication flow...")
    subprocess.check_call([python_exe, "inner_auth.py"])

if __name__ == "__main__":
    create_venv()
    run_auth()
