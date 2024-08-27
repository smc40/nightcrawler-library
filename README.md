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

### Run tests

```sh
python -m pytest -s --cov=libnightcrawler tests
```

