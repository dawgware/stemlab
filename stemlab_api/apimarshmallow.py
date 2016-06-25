from flask_marshmallow import Marshmallow

class ApiMarshmallow(object):

    def __init__(self):
        self._ma = None

    def make_smore(self, app):
        self._ma = Marshmallow(app)

    @property
    def mallow(self):
        return self._ma
