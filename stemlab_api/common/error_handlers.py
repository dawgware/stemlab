from flask import jsonify
from stemlab_api import app

NOT_FOUND = 404


@app.errorhandler(404)
def not_found(error=None):
    if error is None:
        msg = "Not Found"
    else:
        msg = error

    message = {
            'status': 404,
            'message': msg
    }

    return message


@app.errorhandler(409)
def conflict(error=None):
    if error is None:
        msg = "Conflict"
    else:
        msg = error

    message = {
            'status': 409,
            'message': msg
    }

    return message

@app.errorhandler(500)
def internal_error(error=None):
    if error is None:
        msg = "Internal Server Error"
    else:
        msg = error

    message = {
            'status': 500,
            'message': msg
    }

    return message


@app.errorhandler(422)
def handle_bad_request(err):
    # webargs attaches additional metadata to the `data` attribute
    data = getattr(err, 'data')
    if data:
        # Get validations from the ValidationError object
        messages = data['exc'].messages
    else:
        messages = ['Invalid request']
    return jsonify({
        'messages': messages,
    }), 422


class InvalidRequestException(Exception):
    def __init__(self, message=None):
        Exception.__init__(self)
        self.message = message


class NotFoundError(Exception):
    def __init__(self, message=None):
        Exception.__init__(self)
        self.message = message


class ConflictError(Exception):
    def __init__(self, message=None):
        Exception.__init__(self)
        self.message = message
