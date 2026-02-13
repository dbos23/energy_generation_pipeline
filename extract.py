import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import modules
import sys

#create directories for output data and logs if they don't already exist
for dir in ['data', 'logs']:
    os.makedirs(dir, exist_ok=True)

#create timestamp for output file names
current_timestamp = datetime.now()
current_timestamp_str = current_timestamp.strftime('%Y-%m-%d_%H-%M-%S')

#set up logging
logger = modules.make_logger(timestamp=current_timestamp_str)

#load api key and define url for download
load_dotenv()
api_key = os.getenv('api_key')
url = 'https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/'

#the results will be paginated. these variables will account for that pagination
iteration = 0
offset = 0
total_results = 100000 #setting this arbitrarily at first to make sure at least one download always runs

#define number of retries (in the event of server errors in the API)
current_attempt = 0
max_attempts = 3

modules.print_and_log(logger, 'info', 'Starting downloads')

#only continue downloading while there are results left to download and the max attempts haven't been reached
while (offset < total_results) and (current_attempt < max_attempts):
    #define download parameters
    params = {
        'api_key': api_key,
        'frequency': 'daily',
        'data[0]': 'value',
        'offset': offset,
        'length': 5000,
        'facets[respondent][]': 'NY' #filtering to New York only
    }

    try:
        #download data
        response = requests.get(url, params=params)
        response.raise_for_status()

        #write data to file
        modules.write_data_to_file(response, iteration, logger, current_timestamp_str)

        #increment variables. we'll have to paginate the downloads to get them all since one download is limited to 5000 results
        iteration += 1
        offset += 5000

    #handle and log HTTP errors
    except requests.exceptions.HTTPError as e:
        modules.print_and_log(logger, 'error', f'HTTP error during download {iteration}: {response.status_code} {e}')
        if response.status_code >= 500:
            current_attempt += 1
        else:
            modules.print_and_log(logger, 'error', 'Terminating script')
            sys.exit()

    #handle and log any other kinds of errors
    except Exception as e:
        modules.print_and_log(logger, 'error', f'Non-HTTP error during download {iteration}: {e}')
        modules.print_and_log(logger, 'error', 'Terminating script')
        sys.exit()

modules.print_and_log(logger, 'info', 'All results downloaded')