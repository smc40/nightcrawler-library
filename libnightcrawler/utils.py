import requests
import backoff
import hashlib


def get_extension(url: str) -> str:
    return url.split(".")[-1]


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_content(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
