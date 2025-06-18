import logging

def get_logger(name="smart_port_scanner"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler("/var/log/smart_port_scanner.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
