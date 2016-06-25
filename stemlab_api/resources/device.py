import uuid
import traceback
from stemlab_api.database import db, ma
from flask_classful import FlaskView, route
from flask import url_for
from stemlab_api.common.representations import output_json
from stemlab_api.common.args import device_args, device_name_args
from stemlab_api.common.hypermedia_output import create_collection, create_links
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs, parser
from stemlab_api.common.error_handlers import not_found, conflict, internal_error, handle_bad_request
from stemlab_api.common.error_handlers import ConflictError, InvalidRequestException, NotFoundError
from flask import request
from flask_marshmallow.fields import UrlFor, AbsoluteUrlFor
from stemlab_api.models.models import Devices, Readings
from stemlab_api.database import db_client
from stemlab_api.common.db_utils import TEMPERATURE, HUMIDITY
from stemlab_api.common.utils import hasitems
from stemlab_api.resources.readings import (temperature_reading_schema, temperature_readings_schema,
humidity_reading_schema,humidity_readings_schema, get_reading_by_device_and_time, TemperatureReadingsView)


class DevicesSchema(ma.mallow.ModelSchema):
    class Meta:
        model = Devices
        fields = ('device_id', 'device_name', 'location', 'temperature_sensor', 'humidity_sensor', 'uptime', 'url')

device_schema = DevicesSchema()
devices_schema = DevicesSchema(many=True)

class DevicesView(FlaskView):
    representations = {'application/json': output_json}

    def index(self):
        try:
            all_devices = Devices.query.all()
            result = devices_schema.dump(all_devices, many=True)
            collection = create_collection('1.0', request.url, result.data)
        except Exception as e:
            print traceback.format_exc()
            return not_found(), 404
        return collection, 200

    def get(self, device_id):
        items = []
        if device_id is not None and len(device_id) > 0:
            device = Devices.query.filter_by(device_id=device_id).first()
            if device is None:
                device = Devices.query.filter_by(device_name=device_id).first()
                if device is None:
                    return not_found("Device Not Found for "  + device_id + "by id or name"), 404

            device_id = device.device_id
            result = device_schema.dump(device, many=False)
            links = []
            link = create_links('latest', url_for("DevicesView:latest", device_id=device_id, _external=True))
            links.append(link)
            link = create_links(TEMPERATURE, url_for("TemperatureReadingsView:template", device_id=device_id, _external=True))
            links.append(link)
            link = create_links(HUMIDITY, url_for("HumidityReadingsView:template", device_id=device_id, _external=True))
            links.append(link)

            items.append({'data': result.data, 'links': []})
            collection_url = url_for("DevicesView:index", _external=True)
            collection = create_collection('1.0', collection_url, items, links=links)
            return collection, 200

    def post(self):
        args = parser.parse(device_args, request)
        device = Devices.query.filter_by(device_name=args['device_name']).first()
        if device is not None:
            return conflict("Device with name {n} already exists".format(n=args['device_name'])), 409
        try:
            device_id = str(uuid.uuid4())
            location = None
            temperature_sensor = False
            humidity_sensor = False
            uptime = 1
            if 'location' in args:
                location = args['location']
            if 'temperature_sensor' in args:
                temperature_sensor = True
            if 'humidity_sensor' in args:
                humidity_sensor = True
            if 'uptime' in args:
                uptime = long(args['uptime'])
            else:
                uptime = long(0)
            device = Devices(device_id=device_id,
                             device_name=args['device_name'],
                             location=location,
                             temperature_sensor=temperature_sensor,
                             humidity_sensor=humidity_sensor,
                             uptime=uptime)
            db.session.add(device)
            db.session.commit()
            return "Location: " + device.url, 200
        except Exception as e:
            return internal_error("Server Error " + str(e)), 500

    def delete(self):
        args = parser.parse(device_name_args, request)
        device_name = args['device_name']
        if device_name is not None and len(device_name) > 0:
            try:
                device = Devices.query.filter_by(device_name=device_name).first()
                if device is None:
                    return not_found("Device Not Found " + device_name), 404
                db.session.delete(device)
                db.session.commit()
                return "Device Deleted.", 200
            except Exception as e:
                return internal_error("Server Error " + str(e)), 500

    @route('/<device_id>/<datetime>')
    def by_datetime(self, device_id, datetime):
        try:
            if datetime is None:
                raise InvalidRequestException('Missing required datetime value')
            if device_id is None:
                raise InvalidRequestException('Missing required device_id value')

            results = get_reading_by_device_and_time(device_id=device_id,
                                                     timestamp=datetime)

            items, links = generate_reading_response(device_id, results)

            collection_href = url_for("DevicesView:index", _external=True)
            results = create_collection('1.0', collection_href, items, links)
            return results, 200

        except NotFoundError as nfe:
            return not_found('No readings found for device {d} at {t}'
                             .format(d=device_id, t=datetime)), 404
        except InvalidRequestException as ire:
            return handle_bad_request(ire.message), 422
        except Exception as e:
            print traceback.format_exc()
            return internal_error(e.message), 500

    @route('/<device_id>/latest')
    def latest(self, device_id):
        if device_id is not None and len(device_id) > 0:
            items = []
            links = []
            device = Devices.query.filter_by(device_id=device_id).first()
            if device is None:
                return not_found("Device Not Found " + device_id), 404

            result = device_schema.dump(device, many=False)
            item_dict = {'data': result.data, 'links': []}
            items.append(item_dict)
            result_set = get_latest_device_readings(device_id)
            if result_set is not None:
                if TEMPERATURE in dict(result_set.keys()):
                    result_list = list(result_set.get_points(measurement=TEMPERATURE))
                    if hasitems(result_list):
                        for reading in result_list:
                            response_dict, response_errors = temperature_reading_schema.dump(reading)
                            item_dict = {'data': response_dict, 'links': []}
                            items.append(item_dict)
                result_list = []
                if HUMIDITY in dict(result_set.keys()):
                    result_list = list(result_set.get_points(measurement=HUMIDITY))
                    if hasitems(result_list):
                        for reading in result_list:
                            response_dict, response_errors = humidity_reading_schema.dump(reading)
                            item_dict = {'data': response_dict, 'links': []}
                            items.append(item_dict)
            collection_url = url_for("DevicesView:latest", device_id=device_id, _external=True)
            collection = create_collection('1.0', collection_url, items, links)
            # return result.data, 200
            return collection, 200


def get_latest_device_readings(device_id):
    result = None
    if device_id is not None:
        query = "SELECT log_id,device_id,value,time FROM temperature,humidity WHERE device_id='{device}' " \
                "ORDER BY time DESC LIMIT 1 SLIMIT 1;".format(device=device_id)
        print query
        result = db_client.get_reading_with_sql(query=query)
    return result


def generate_reading_response(device_id, results):
    items = []
    item_dict = {}
    links = []
    item_links = []
    reading = None
    if results is None or len(results.keys()) == 0:
        raise NotFoundError()
    ref_url = url_for("DevicesView:get", device_id=device_id, _external=True)
    link_dict = create_links('device', ref_url)
    links.append(link_dict)
    for measurement in [TEMPERATURE, HUMIDITY]:
        result_list = list(results.get_points(measurement=measurement))
        for reading in result_list:
            response_dict = None
            if measurement == TEMPERATURE:
                response_dict, response_errors = temperature_reading_schema.dump(reading)
            else:
                response_dict, response_errors = humidity_reading_schema.dump(reading)
            item_dict['data'] = response_dict
            item_dict['links'] = item_links
            items.append(item_dict)
    return items, links

