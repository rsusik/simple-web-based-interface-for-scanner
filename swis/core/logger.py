
from functools import lru_cache
import logging


@lru_cache
def get_logger():
    log = logging.getLogger('uvicorn')
    log.propagate = False
    return log