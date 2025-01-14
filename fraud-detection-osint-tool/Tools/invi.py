import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
API_KEY = os.getenv("HIBP_API_KEY")
BASE_URL = "https://haveibeenpwned.com/api/v3"

def check_breach(account):
    url = f"{BASE_URL}/breachedaccount/{account}"
    headers = {
        "hibp-api-key": API_KEY,
        "User-Agent": "PythonApp"  # Required by HIBP API
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # List of breaches
    elif response.status_code == 404:
        return f"No breaches found for {account}"
    else:
        return f"Error: {response.status_code} - {response.text}"

# Test the function
email = "test@example.com"
result = check_breach(email)
print(result)