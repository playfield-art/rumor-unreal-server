# Installation

## Make a new virtual environment

e.g. on windows

```python -m venv venv```

## Upgrade pip

```python.exe -m pip install --upgrade pip```

## Install dependencies

```pip install -r requests.txt```

or the other way

```pip install "fastapi[all]" requests APScheduler```

## Running server

```uvicorn main:app --reload```

## Make requests 

Endpoints 

- http://127.0.0.1:8000/api/data
- http://127.0.0.1:8000/api/categories

