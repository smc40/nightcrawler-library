import requests
import backoff
import hashlib


def get_extension(url: str) -> str:
    return url.split(".")[-1]


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5)
def get_content(url: str) -> tuple[bytes, str|None]:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    return response.content, response.headers.get("Content-Type")


def checksum(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()
