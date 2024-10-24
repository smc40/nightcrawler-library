# nightcrawler-library

## Scope

- Entities definition
- Entities storage
- Cost reporting
- User preferences
- Configurations
- Notifications I/O

## Local development

### Requirements

- python3
- docker

### Setup

```sh
sudo apt-get install libpq-dev
python3 -m venv venv
source venv/bin/activate
pip install poetry
poetry install
```

Note to debian users:

```sh
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```

### Services

```sh
docker run -i -d \
    --name nightcrawler \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_USER=user \
    -e POSTGRES_DB=nightcrawler \
    -p 5432:5432 \
    citusdata/citus:12.1
```

```sh
docker run -i -d \
     --name azurite \
     -p 10000:10000 -p 10001:10001 -p 10002:10002 \
     mcr.microsoft.com/azure-storage/azurite
```

Create 3 containers:

```sh
for blob in images processing public;do docker run -it --rm --network host mcr.microsoft.com/azure-cli az storage container create -n ${blob} --connection-string "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;";done;
```

### Run tests

```sh
python -m pytest -s --cov=libnightcrawler tests
```

