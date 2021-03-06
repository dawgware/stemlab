from flask_restful import Resource
import uuid
from stemlab_api.database import db
from stemlab_api.api import ma
from stemlab_api.models.models import Readings, Devices
from flask_classful import FlaskView, route
from flask import url_for
from stemlab_api.common.representations import output_json
from stemlab_api.common.args import reading_args
from stemlab_api.common.hypermedia_output import create_collection
from stemlab_api.api import db_client
from stemlab_api.resources.device import Devices
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs, parser
from stemlab_api.common.error_handlers import not_found, conflict, internal_error
from stemlab_api.common.db_utils import DBUtils
from flask import request
from flask_marshmallow import Schema
from marshmallow import fields
from collections import OrderedDict
from flask_marshmallow.fields import UrlFor, AbsoluteUrlFor
from path import Path
from arrow import Arrow
import json
import decimal

readings = OrderedDict()
input_file = Path.joinpath(app.root_path, '.readings.log')
if input_file.isfile():
    with input_file.open('rb') as input:
        readings = json.load(input)



class ReadingsSchema(Schema):
    class Meta:
        fields = ("log_id", "device_id", "temperature", "humidity", "timestamp", "url")
    # log_id = fields.UUID()
    # device_id = fields.UUID()
    # temperature = fields.Decimal()
    # humidity = fields.Decimal()
    # timestamp = fields.DateTime()
    # url = fields.Url()

reading_schema = ReadingsSchema()
readings_schema = ReadingsSchema(many=True)


class ReadingsView(FlaskView):
    representations = {'application/json': output_json}

    def index(self):
        try:
            if readings is not None and len(readings) > 0:
                return readings, 200
            else:
                return not_found(), 404
        except Exception as e:
            return not_found(), 404

    def get(self, log_id):
        if log_id is not None and len(log_id) > 0:
            reading = None
            if len(readings) > 0:
                try:
                    reading = readings[log_id]
                except KeyError as ke:
                    return not_found(), 404
                results = create_collection('1.0', request.url_root, reading)
                return results, 200

    def post(self):
        args = parser.parse(reading_args)
        # if reading_search(args['device_id'], args['timestamp']):
        #     return conflict("Record already exists for device {d} at time {t}".format(d=args['device_id'],
        #                                                                     t=args['timestamp'])), 409
        log_id = uuid.uuid4()
        humidity = args['humidity'] if 'humidity' in args else 0.0

        reading = Readings(log_id=log_id,
                           temperature=args['temperature'],
                           humidity=humidity,
                           device_id=args['device_id'],
                           timestamp=args['timestamp']
                           )
        # result_json = reading_schema.dump(reading).data
        save_reading(reading)

        # collection = create_collection('1.0', request.url, result)
        return "Location: " + reading.url, 200

def save_reading(reading):
    if reading is not None:
        record = reading.db_record()
        db_client.insert_reading(record)

def reading_exist(device_id, timestamp):
    result = False
    if device_id is not None and timestamp is not None:
        result = db_client.get_reading_by_device_time(device_id, timestamp)
        if result is not None and len(result) > 0:
            return True

def get_device_readings(device_id):
    result = None
    if device_id is not None:
        result = db_client.get_device_readings(device_id)
    return result

# def reading_search(device_id, timestamp):
#     if readings is not None and len(readings) > 0:
#         for log_id, reading in readings.items():
#             values = reading.values()
#             if device_id in values and timestamp in values:
#                 return True


# def save_reading(reading):
#     if reading is not None and isinstance(reading, dict):
#         if reading['log_id'] in readings:
#             return False
#
#         readings[reading['log_id']] = reading
#         write_to_file()


def write_to_file():
    output_file = Path.joinpath(app.root_path, '.readings.log')
    with output_file.open('wb') as output:
        json_data=json.dumps(readings, indent=4, encoding="utf-8", cls=DecimalEncoder)
        print >> output, json_data


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)