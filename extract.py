import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import modules

#create directories for output data and logs. create timestamp for output file names
for dir in ['data', 'logs']:
    os.makedirs(dir, exist_ok=True)
current_timestamp = datetime.now()
current_timestamp_str = current_timestamp.strftime('%Y-%m-%d_%H-%M-%S')

#set up logging
logger = modules.make_logger(timestamp=current_timestamp_str)

#load api key
load_dotenv()
api_key = os.getenv('api_key')

#define url for download
url = 'https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/'

#the results will be paginated. these variables will account for that pagination
iteration = 0
offset = 0
total_results = 100000 #setting this arbitrarily at first to make sure at least one download always runs

modules.print_and_log(logger, 'info', 'Starting downloads')

while offset < total_results:
    #define download parameters
    params = {
        'api_key': api_key,
        'frequency': 'daily',
        'data[0]': 'value',
        'offset': offset,
        'length': 5000,
        'facets[respondent][]': 'NY' #filtering to New York only
    }

    #download results
    response = requests.get(url, params=params)
    data = response.json()

    #set total_results to its true value. print the proportion of results downloaded
    total_results = int(data['response']['total'])
    results_downloaded = (5000 * iteration) + 5000
    modules.print_and_log(logger, 'info', f'Download {iteration} complete. {results_downloaded} out of {total_results} results downloaded')

    #write results to file
    output_file_name = current_timestamp_str + '_' + str(iteration) + '.json'

    with open(f'data/{output_file_name}', 'w') as json_file:
        json.dump(data, json_file)

    modules.print_and_log(logger, 'info', f'File {iteration} written to {output_file_name}')

    #increment variables. we'll have to paginate the downloads to get them all since one download is limited to 5000 results
    iteration += 1
    offset += 5000

modules.print_and_log(logger, 'info', 'All results downloaded')