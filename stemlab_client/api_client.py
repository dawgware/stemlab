"""
    Created: June 22, 2016
    Author: Carl Wilen

    Provides client access to remote API server. Supports GET, POST, PUT and DELETE methods. All methods return
    a requests.response object.
"""
import requests

__version__ = 1.0
__author__ = "dawgwaredev@gmail.com"

def get(url, params=None):
    """
    Peforms an http GET on the passed URL
    :param url: GET endpoint
    :param params: key,value collection for query string
    :return: requests.response object containing Collection+JSON formatted response.
    """
    response = None
    if params is None:
        response = requests.get(url, timeout=5)
    else:
        response = requests.get(url, params=params, timeout=5)

    return response


def post(url, data):
    """
    Performs an HTTP POST to the passed url endpoint using the
    values in the data parameter.
    :param url: POST endpoint
    :param data: key, value collection for query string
    :return: requests.response object with link to created object.
    """

    response = None
    if data is None:
        raise ValueError("Data values required for post")

    response = requests.post(url, data=data, timeout=5)

    return response

