import requests
from .errors import ShareplumRequestError


def get(session, url, **kwargs):
    try:
        response = session.get(url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        raise ShareplumRequestError("Shareplum HTTP Get Failed", err)


def post(session, url, **kwargs):
    try:
        response = session.post(url, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        raise ShareplumRequestError("Shareplum HTTP Post Failed", err)
