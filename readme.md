# Installation

## Make a new virtual environment

e.g. on windows

```python -m venv venv```

## Activate environment

e.g on windows

```venv\Scripts\activate```

e.g. on mac

```source venv/bin/activate```

## Upgrade pip

```python.exe -m pip install --upgrade pip```

## Install dependencies

```pip install -r requirements.txt```

or the other way

```pip install "fastapi[all]" requests APScheduler```

## Running server

```venv\Scripts\activate```
```uvicorn main:app --reload```

## Make requests 

Endpoints 

- http://127.0.0.1:8000/api/data
- http://127.0.0.1:8000/api/categories

