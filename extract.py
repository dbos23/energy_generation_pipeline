import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

#load api key
load_dotenv()
api_key = os.getenv('api_key')

#define url for download
url = 'https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/'

#create directory for output data and timestamp for output file names
os.makedirs('data', exist_ok=True)
current_timestamp = datetime.now()
current_timestamp_str = current_timestamp.strftime('%Y-%m-%d_%H-%M-%S')

#the results will be paginated. these variables will account for that pagination
iteration = 0
offset = 0
total_results = 100000 #setting this arbitrarily at first to make sure at least one download always runs

while offset < total_results:
    #define download parameters
    params = {
        'api_key': api_key,
        'frequency': 'daily',
        'data[0]': 'value',
        'offset': offset,
        'length': 5000
    }

    #download results and write to file
    response = requests.get(url, params=params)
    data = response.json()
    output_file_name = current_timestamp_str + '_' + str(iteration) + '.json'

    with open(f'data/{output_file_name}', 'w') as json_file:
        json.dump(data, json_file)

    #increment variables and set the total_results variable to its true value. we'll have to paginate the downloads to get them all since one download is limited to 5000
    iteration += 1
    offset += 5000
    total_results = int(data['response']['total'])