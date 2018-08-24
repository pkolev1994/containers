from lib.logger import Logger


logger = Logger()
logger.error("BLQ BLA")
logger.info("BLQ asdfsdf")
logger.critical("BLQ sdfasdfasd")

# import logging

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# # create the logging file handler
# fh = logging.FileHandler("new_snake.log")

# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)

# # add handler to logger object
# logger.addHandler(fh)

# logger.info("Program started")