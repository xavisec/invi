import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
API_KEY = os.getenv("HIBP_API_KEY")
BASE_URL = "https://haveibeenpwned.com/api/v3"


def get_breached_data(account):
    url = f"{BASE_URL}/breachedaccount/{account}?truncateResponse=false"
    headers = {
        "hibp-api-key": API_KEY,
        "User-Agent": "PythonApp"  # Required by HIBP API
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        breaches = response.json()
        for breach in breaches:
            print(f"Name: {breach.get('Name', 'N/A')}")
            print(f"Title: {breach.get('Title', 'N/A')}")
            print(f"Domain: {breach.get('Domain', 'N/A')}")
            print(f"Breach Date: {breach.get('BreachDate', 'N/A')}")
            print(f"Description: {breach.get('Description', 'N/A')}")
            print(f"Compromised Data: {', '.join(breach.get('DataClasses', []))}")
            print(f"PwnCount: {breach.get('PwnCount', 'N/A')}")
            print("-" * 40)
    elif response.status_code == 404:
        print(f"No breaches found for {account}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# Replace it with the account
email = "example"
get_breached_data(email)