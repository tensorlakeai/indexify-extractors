from itertools import islice
import requests
import platform
import fsspec
import json

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
            "https://getindexify.ai/api/analytics", json={"event": event, "value": value, "platform":platform.platform(), "machine": platform.machine()}
        , timeout=1)
    except Exception as e:
        # fail silently
        pass

def read_extractors_json_file(filename):
    # # debug
    # with open(filename, "r") as file:
    #     json_content = json.load(file)
    # return json_content

    fs = fsspec.filesystem("github", org="tensorlakeai", repo="indexify-extractors")
    file_path = filename

    with fs.open(file_path, "r") as file:
        # Load the JSON content from the file
        json_content = json.load(file)

    return json_content

