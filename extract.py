import requests
import os
from dotenv import load_dotenv

#load api key
load_dotenv()
api_key = os.getenv('api_key')

#define url and request parameters
url = 'https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/'
params = {
    'api_key': api_key,
    'frequency': 'daily',
    'data[0]': 'value',
    'offset': 0
}

response = requests.get(url, params=params)

print(response)
print(response.reason)