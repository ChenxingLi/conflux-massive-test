import inspect
import time

from loguru import logger

class WaitUntilTimeoutError(Exception):
    pass

def wait_until(predicate,
               *,
               attempts=float('inf'),
               timeout=float('inf'),
               retry_interval=0.5,
               lock=None):
    if attempts == float('inf') and timeout == float('inf'):
        timeout = 60
    attempt = 0
    time_end = time.time() + timeout

    while attempt < attempts and time.time() < time_end:
        if lock:
            with lock:
                if predicate():
                    return
        else:
            if predicate():
                return
        attempt += 1
        time.sleep(retry_interval)

    # Print the cause of the timeout
    predicate_source = inspect.getsourcelines(predicate)
    logger.warning(
        "wait_until() failed. Predicate: {}".format(predicate_source))
    if attempt >= attempts:
        raise WaitUntilTimeoutError(
            "Predicate {} not true after {} attempts".format(
                predicate_source, attempts))
    elif time.time() >= time_end:
        raise WaitUntilTimeoutError(
            "Predicate {} not true after {} seconds".format(
                predicate_source, timeout))
    raise RuntimeError('Unreachable')
