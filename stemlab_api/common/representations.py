import json
from flask import make_response
import decimal


def output_json(data, code, headers=None):
    content_type = 'application/json'
    dumped = json.dumps(data, cls=DecimalEncoder)
    if headers:
        headers.update({'Content-Type': content_type})
    else:
        headers = {'Content-Type': content_type}
    response = make_response(dumped, code, headers)
    return response


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)