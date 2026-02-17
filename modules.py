import logging
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




def upload_to_s3(json_string, total_results, iteration, logger, timestamp, client, s3_bucket_name):
        '''
        Uploads the downloaded data to the selected S3 bucket as a JSON file. Prints and logs outcomes
        '''
        #print and log the proportion of results downloaded
        results_downloaded = (5000 * iteration) + 5000
        if results_downloaded > total_results:
            results_downloaded = total_results

        print_and_log(logger, 'info', f'Download {iteration} complete. {results_downloaded} out of {total_results} results downloaded')

        #upload results to s3
        output_file_name = timestamp + '_' + str(iteration) + '.json'
        client.put_object(Body=json_string, Bucket=s3_bucket_name, Key=output_file_name)

        print_and_log(logger, 'info', f'File {iteration} written to S3 at {s3_bucket_name}/{output_file_name}')