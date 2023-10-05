import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_version(module_name: str):
    return module_name.split(".")[2]
