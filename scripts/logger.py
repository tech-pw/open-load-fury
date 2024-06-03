import logging

def setup_logger(log_file_path):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s: %(levelname)s: %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file_path)
        ]
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_format = logging.Formatter('%(levelname)s: %(name)s: %(message)s')
    console_handler.setFormatter(console_format)

    logger = logging.getLogger()
    logger.addHandler(console_handler)

    return logger
