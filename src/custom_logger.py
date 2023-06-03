import logging

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler to write logs to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Create a formatter for the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Get the root logger
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)