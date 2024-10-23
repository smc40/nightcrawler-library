import requests
import backoff
import hashlib


def get_extension(url: str) -> str:
    return url.split(".")[-1]


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_content(url: str) -> bytes:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content


def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
