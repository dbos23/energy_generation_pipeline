import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import boto3
import requests
import json
import modules

#create directories for output data and logs if they don't already exist
for dir in ['data', 'logs']:
    os.makedirs(dir, exist_ok=True)

#create timestamp for output file names and download parameters
current_timestamp = datetime.now()
current_timestamp_str = current_timestamp.strftime('%Y-%m-%d_%H-%M-%S')

#load environment variables, set variables to use for download
load_dotenv()
aws_access_key = os.getenv('aws_access_key')
aws_secret_key = os.getenv('aws_secret_key')
s3_bucket_name = os.getenv('s3_bucket_name')
api_key = os.getenv('api_key')
url = 'https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/'
download_date = str(current_timestamp - timedelta(days=1))[:10] #yesterday's date

#set variables for retries and pagination
max_attempts = 3
current_attempt = iteration = offset = 0
total_results = 100000 #setting this arbitrarily at first to make sure at least one download always runs. it'll be overwritten with the true value during the download

#set up logging
logger = modules.make_logger(timestamp=current_timestamp_str)

#connect to s3
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

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
        'start': download_date,
        'end': download_date,
        'facets[respondent][]': 'NY' #filtering to New York only
    }

    try:
        #download data
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        json_string = json.dumps(data)

        #set total_results to its true value
        total_results = int(data['response']['total'])

        #upload json data to s3 bucket
        modules.upload_to_s3(json_string, total_results, iteration, logger, current_timestamp_str, s3_client, s3_bucket_name)

        #increment variables. we may have to paginate the downloads to get everything since one download is limited to 5000 results
        iteration += 1
        offset += 5000

    #handle and log HTTP errors
    except requests.exceptions.HTTPError as e:
        modules.print_and_log(logger, 'error', f'HTTP error during download {iteration}: {response.status_code} {e}')
        if response.status_code >= 500:
            current_attempt += 1
            if current_attempt >= 3:
                modules.print_and_log(logger, 'error', 'Terminating script')
                sys.exit()
        else:
            modules.print_and_log(logger, 'error', 'Terminating script')
            sys.exit()

    #handle and log any other kinds of errors
    except Exception as e:
        modules.print_and_log(logger, 'error', f'Non-HTTP error during download {iteration}: {e}')
        modules.print_and_log(logger, 'error', 'Terminating script')
        sys.exit()

modules.print_and_log(logger, 'info', 'All results downloaded')