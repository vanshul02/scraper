import logging

class LogUtil:
    def __init__(self, file_name = None):
        handlers = [logging.StreamHandler()]
        if file_name is not None: handlers.append(logging.FileHandler(file_name, 'w'))
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s-%(levelname)s-%(name)s :: %(message)s',
            handlers=handlers
        )

    def get_logger(self, name: str):
        return logging.getLogger(name)