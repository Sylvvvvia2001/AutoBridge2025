import requests
import yaml

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Ezviz API Information
API_URL = "https://open.ys7.com/api/lapp/token/get"
API_KEY = config['ezviz']['api_key']
DEVICE_SERIAL = config['ezviz']['device_serial']
ACCOUNT = config['ezviz']['account']
PASSWORD = config['ezviz']['password']

def get_access_token():
    """Get the access token from Ezviz API."""
    payload = {
        'appKey': API_KEY,
        'appSecret': PASSWORD
    }
    response = requests.post(API_URL, data=payload)
    if response.status_code == 200:
        return response.json()['data']['accessToken']
    else:
        print("Failed to get access token")
        return None

def main():
    access_token = get_access_token()
    if access_token:
        print("Access Token:", access_token)
        # Add further operations here, like live view, device control, etc.

if __name__ == "__main__":
    main()
