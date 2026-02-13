import logging
import requests
import json




def make_logger(timestamp):
    '''
    Creates a logger, using a timestamp as a suffix to make the file name unique
    '''
    log_filepath = f'logs/{timestamp}.log'

    #set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_filepath
    )
    return logging.getLogger()




def print_and_log(logger, severity, message):
    '''
    Outputs the same message to the terminal and the logs
    '''
    print(message)
    if severity == 'debug':
        logger.debug(message)
    elif severity == 'info':
        logger.info(message)
    elif severity == 'warning':
        logger.warning(message)
    elif severity == 'error':
        logger.error(message)
    elif severity == 'critical':
        logger.critical(message)




def write_data_to_file(response, iteration, logger, timestamp):
        '''
        Outputs the downloaded data as a JSON file. Prints and logs outcomes and defines the total_results variable, which is used for the download pagination
        '''
        #error if there's an HTTP error
        data = response.json()

        #set total_results to its true value. print and log the proportion of results downloaded
        total_results = int(data['response']['total'])
        results_downloaded = (5000 * iteration) + 5000
        print_and_log(logger, 'info', f'Download {iteration} complete. {results_downloaded} out of {total_results} results downloaded')

        #write results to file
        output_file_name = timestamp + '_' + str(iteration) + '.json'

        with open(f'data/{output_file_name}', 'w') as json_file:
            json.dump(data, json_file)

        print_and_log(logger, 'info', f'File {iteration} written to {output_file_name}')