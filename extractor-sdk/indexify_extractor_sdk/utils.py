from itertools import islice
import requests


# https://docs.python.org/3/library/itertools.html#itertools.batched
def batched(iterable, n):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def log_event(event, value):
    try:
        requests.post(
            "https://www.tensorlake.ai/api/analytics", json={"event": event, "value": value}
        )
    except Exception as e:
        # fail silently
        pass
