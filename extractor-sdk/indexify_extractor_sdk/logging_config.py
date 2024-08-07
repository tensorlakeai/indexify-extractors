import logging
from logging.handlers import RotatingFileHandler

def configure_logging(level=logging.INFO):
    logger = logging.getLogger('indexify_extractor')
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = RotatingFileHandler('indexify_extractor.log', maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = configure_logging()