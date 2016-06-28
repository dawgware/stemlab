from flask_restful import Resource
from stemlab_api.database import db
from stemlab_api.resources.device import Devices
from webargs import fields
from marshmallow import fields
from flask_marshmallow.fields import UrlFor, AbsoluteUrlFor
from arrow import Arrow
import uuid
import traceback
from stemlab_api.models.models import TemperatureReadings, HumidityReadings, reading_factory
from stemlab_api.common.representations import output_json, DecimalEncoder
from stemlab_api.common.args import temperature_reading_args, humidity_reading_args, reading_args
from stemlab_api.common.hypermedia_output import create_collection, create_links, create_template
from stemlab_api.database import db_client
from stemlab_api.common.error_handlers import not_found, conflict, internal_error, handle_bad_request
from stemlab_api.common.error_handlers import InvalidRequestException, NotFoundError, ConflictError
from stemlab_api.common.db_utils import TEMPERATURE, HUMIDITY
from stemlab_api import app
from stemlab_api.common.utils import query_timestamp, convert_to_timestamp
from stemlab_api.database import ma
from webargs.flaskparser import use_args, use_kwargs, parser
from flask_classful import FlaskView, route
from flask import request, url_for
from collections import OrderedDict
from path import Path
import json
import decimal

__author__='dawaredev@gmail.com'

readings = OrderedDict()
input_file = Path.joinpath(app.root_path, '.readings.log')
if input_file.isfile():
    with input_file.open('rb') as input:
        readings = json.load(input)


class TemperatureReadingsSchema(ma.mallow.Schema):
    # class Meta:
        # fields = ("log_id", "device_id", "temperature", "time", "url")
    log_id = fields.UUID()
    device_id = fields.UUID()
    temperature = fields.Decimal(attribute='value')
    timestamp = fields.Method('get_time')
    device_name = fields.String()
    location = fields.String()
    units = fields.String()
    url = ma.mallow.URLFor('TemperatureReadingsView:get', log_id='<log_id>', _external=True)

    def get_time(self, obj):
        return obj['time']

temperature_reading_schema = TemperatureReadingsSchema()
temperature_readings_schema = TemperatureReadingsSchema(many=True)


class TemperatureReadingsView(FlaskView):
    representations = {'application/json': output_json}
    route_base = 'temperature'
    route_prefix = 'readings'

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
            items = []
            links = []
            try:
                items, links = generate_get_response(log_id, TEMPERATURE, temperature_reading_schema)

            except KeyError as ke:
                print traceback.format_exc()
                return not_found(), 404
            except Exception as e:
                print traceback.format_exc()
                return internal_error(), 500

            collection_href = url_for("TemperatureReadingsView:index", _external=True)
            results = create_collection('1.0', collection_href, items, links)
            return results, 200

    def post(self):
        try:
            # args = parser.parse(temperature_reading_args)
            args = parser.parse(reading_args)
            log_id = post_reading(args, TEMPERATURE)
            return "Location: " + url_for("TemperatureReadingsView:get", log_id=log_id, _external=True), 200
        except InvalidRequestException as ire:
            return handle_bad_request(ire.message), 422
        except NotFoundError as nfe:
            return not_found(nfe.message), 404
        except Exception as e:
            print traceback.format_exc()
            return internal_error(), 500

    def template(self, device_id):
        try:
            template_args = {'device_id': device_id}
            for arg in [arg for arg in reading_args.keys() if arg is not 'device_id']:
                template_args[arg] = ""
            template_collection = create_template('1.0',
                                                  url_for("TemperatureReadingsView:index", _external=True),
                                                  template_args)
            return template_collection, 200
        except Exception as e:
            return internal_error, 500

class HumidityReadingsSchema(ma.mallow.Schema):
    # class Meta:
    #     fields = ("log_id", "device_id", "humidity", "time", "url")
    log_id = fields.UUID()
    device_id = fields.UUID()
    humidity = fields.Decimal(attribute='value')
    timestamp = fields.Method('get_time')
    device_name = fields.String()
    location = fields.String()
    units = fields.String()
    url = ma.mallow.URLFor('HumidityReadingsView:get', log_id='<log_id>', _external=True)

    def get_time(self, obj):
        return obj['time']

humidity_reading_schema = HumidityReadingsSchema()
humidity_readings_schema = HumidityReadingsSchema(many=True)


class HumidityReadingsView(FlaskView):
    representations = {'application/json': output_json}
    route_base = 'humidity'
    route_prefix = 'readings'

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
            items = []
            links = []
            try:
                items, links = generate_get_response(log_id, HUMIDITY, humidity_reading_schema)
            except KeyError as ke:
                return not_found(), 404
            except Exception as e:
                return internal_error(), 500

            collection_href = url_for("HumidityReadingsView:index", _external=True)
            results = create_collection('1.0', collection_href, items, links)
            return results, 200

    def post(self):
        try:
            args = parser.parse(reading_args)
            log_id = post_reading(args, HUMIDITY)
            return "Location: " + url_for("HumidityReadingsView:get", log_id=log_id, _external=True), 200
        except InvalidRequestException as ire:
            return handle_bad_request(ire.message), 422
        except NotFoundError as nfe:
            return not_found(nfe.message), 404
        except Exception as e:
            print traceback.format_exc()
            return internal_error(), 500

    def template(self, device_id):
        try:
            template_args = {'device_id': device_id}
            for arg in [arg for arg in reading_args.keys() if arg is not 'device_id']:
                template_args[arg] = ""
            template_collection = create_template('1.0',
                                                  url_for("HumidityReadingsView:index", _external=True),
                                                  template_args)
            return template_collection, 200
        except Exception as e:
            return internal_error, 500


def post_reading(args, measurement):
    device_id = None
    timestamp = convert_to_timestamp(str(args['timestamp']))
    device = None
    if 'device_id' in args:
        device = Devices.query.filter_by(device_id=args['device_id']).first()
        if device is not None:
            device_id = device.device_id
        else:
            raise NotFoundError('No device found for device id {id}. Please register this device'
                                .format(id=args['device_id']))
    location = str(device.location)
    device_name = str(device.device_name)
    log_id = str(uuid.uuid4())
    related_measurement = HUMIDITY
    if measurement == HUMIDITY:
        related_measurement = TEMPERATURE

    related_reading = get_reading_by_device_and_time(device_id, timestamp, related_measurement)
    if related_reading is not None and len(related_reading.keys()) > 0:
        points = list(related_reading.get_points())
        single_reading = None
        if len(points) == 1:
            single_reading = points[0]
        else:
            pass
            # TODO: Log that more than one reading exists for same device and timestamp
        if single_reading is not None:
            log_id = single_reading['log_id']

    reading = reading_factory(log_id=log_id,
                              value=args['measurement'],
                              device_id=device_id,
                              timestamp=timestamp,
                              measurement=measurement,
                              device_name=device_name,
                              location=location,
                              units=args['units'])

    existing_log_id = reading_exists(device_id, timestamp, measurement)
    if existing_log_id is None:
        if not save_reading(reading, measurement):
            raise Exception("Unable to save reading. " + reading.db_record())
    else:
        return existing_log_id
    return log_id


def generate_get_response(log_id, measurement, schema):
    try:
        items = []
        item_dict = {}
        links = []
        item_links = []
        reading = None
        result_set = get_reading_by_log_id(log_id, "{t},{h}".format(t=TEMPERATURE,h=HUMIDITY))
        result_list = list(result_set.get_points(measurement=measurement))
        if len(result_list) >= 1:
            # TODO: Log that we got more than temperature reading for a log_id
            reading = result_list[0]
        else:
            raise KeyError()
        device_id = reading['device_id']
        response_dict, response_errors = schema.dump(reading)
        rel_measurement = HUMIDITY
        rel_view = "HumidityReadingsView:get"
        if measurement == HUMIDITY:
            rel_measurement = TEMPERATURE
            rel_view = "TemperatureReadingsView:get"
        if rel_measurement in dict(result_set.keys()):
            ref_url = url_for(rel_view, log_id=log_id, _external=True)
            ref_dict = create_links(rel_measurement, ref_url)
            item_links.append(ref_dict)
        ref_url = url_for("DevicesView:get", device_id=device_id, _external=True)
        link_dict = create_links('device', ref_url)
        links.append(link_dict)
        item_dict['data'] = response_dict
        item_dict['links'] = item_links
        items.append(item_dict)
    except KeyError as ke:
        raise ke
        # return not_found(), 404
    except Exception as e:
        print traceback.format_exc()
        raise e
    return items, links


def save_reading(reading, measurement):
    if reading is not None:
        record = reading.db_record()
        return db_client.insert_reading(record)
    else:
        raise ValueError("Reading instance cannot be None")


def reading_exists(device_id, timestamp, measurement=None):
    ret_log_id = None
    result = get_reading_by_device_and_time(device_id, timestamp, measurement)
    if result is not None and len(result) > 0:
        points = list(result.get_points())
        if len(points) == 1:
            single_reading = points[0]
            if single_reading is not None:
                ret_log_id = single_reading['log_id']
        else:
            pass
            # TODO: Log that more than one reading exists for same device and timestamp
    return ret_log_id


def get_reading_by_device_and_time(device_id, timestamp, measurement=None):
    result = None
    if device_id is not None and timestamp is not None:
        result = db_client.get_reading_by_device_time(device_id, timestamp, measurement)
    return result


def get_reading_by_log_id(log_id, measurement):
    result = None
    if log_id is not None:
        result = db_client.get_reading_by_log_id(log_id, measurement)
    return result


def get_device_readings(device_id, measurement):
    result = None
    if device_id is not None:
        result = db_client.get_device_readings(device_id)
    return result


def write_to_file():
    output_file = Path.joinpath(app.root_path, '.readings.log')
    with output_file.open('wb') as output:
        json_data=json.dumps(readings, indent=4, encoding="utf-8", cls=DecimalEncoder)
        print >> output, json_data

