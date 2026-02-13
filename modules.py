import logging

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