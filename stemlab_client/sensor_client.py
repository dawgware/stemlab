"""
    Created: June 21, 2016
    Author: Carl Wilen

    This is the main module for the sensor client. Runs on the device that's connected to sensors.
    Responsible for command and control of sensor read/report process.

"""
from concurrent.futures import ThreadPoolExecutor
import time
import argparse
import shelve
from arrow import Arrow
import arrow
import traceback
from path import Path
from collection_json import Collection
from stemlab_client.common.measurement_types import FAHRENHEIT, CELSIUS
from stemlab_client.sensors.dht22_sensor_simulator import DHT22Sensor
from stemlab_client.device import Device
from stemlab_client.api_client import get, post
from stemlab_client.common.utils import generate_measurement_params, hasitems, GracefulExit
import sys

__version__ = 1.0
__author__ = "dawgwaredev@gmail.com"

def callback_reading_post(future):
    post_response = future.result()
    print "Reading Response: ", post_response.status_code, post_response.text


def callback_reading_get(future):
    pass


def post_readings(templates, readings):
    if hasitems(templates) and hasitems(readings):
        for reading in readings:
            template = templates[reading.measurement_type.name]
            post_data = generate_measurement_params(template, reading)


class SensorClient(object):

    _device_settings = None
    _db_filename = Path('sensor_client.db')
    SETTINGS_KEY = 'device_settings'
    SENSORS_KEY = 'sensors'

    def __init__(self, api_host,
                 poll_interval,
                 **kwargs):
        self.api_host = api_host
        self.poll_interval = int(poll_interval)
        self.api_port = 80
        self.device_name = None
        self.username = None
        self.password = None
        self.device_location = None
        self.simulate_sensor = False
        self.sensors = []
        if kwargs is not None:
            if 'api_port' in kwargs:
                self.api_port = kwargs['api_port']

            if 'device_name' in kwargs:
                self.device_name = kwargs['device_name']

            if 'device_loc' in kwargs:
                self.device_location = kwargs['device_loc']

            if 'username' in kwargs:
                self.username = kwargs['username']

            if 'password' in kwargs:
                self.password = kwargs['password']

            if 'sim_sensor' in kwargs:
                self.simulate_sensor = True

            self.app_dir = Path('/opt/stemlab')
            if not self.app_dir.isdir():
                self.app_dir = Path.getcwd()


    def _load_persistent_data(self):
        shelve_db = shelve.open(str(Path.joinpath(self.app_dir, self._db_filename)))
        if self.SETTINGS_KEY in shelve_db:
            self._device_settings = shelve_db[self.SETTINGS_KEY]

        shelve_db.close()

    def _register_device(self):
        post_url = "http://{host}:{port}/devices/".format(host=self._device_settings.api_host,
                                                         port=self._device_settings.api_port)
        post_data = {'device_name': self._device_settings.device_name,
                     'humidity_sensor': 'true',
                     'temperature_sensor': 'true',
                     'location': self._device_settings.device_loc,
                     'uptime': 0}
        try:
            reg_response = post(url=post_url, data=post_data)
            if reg_response.status_code == 200:
                loc_text = reg_response.text
                if 'http' in loc_text:
                    loc_url = loc_text[loc_text.index('http'):-1]
                    if loc_url is not None:
                        self._device_settings.device_url = loc_url
            elif reg_response.status_code == 409:
                err_msg = '''
                Unable to register this device with server.
                A device with the name {dn} is already registered.
                Please select another name for device and restart client.
                '''.format(dn=self._device_settings.device_name)
                raise Exception(err_msg)
            else:
                err_msg = '''
                Unable to register this device. Server returned following error;
                {code} {error}
                '''.format(code=reg_response.status_code,
                           error=reg_response.text)
                raise Exception(err_msg)
            return True
        except Exception as e:
            print traceback.format_exc()
            raise e

    def _init_settings(self):
        self._device_settings = Device(api_host=self.api_host,
                                       api_port=self.api_port,
                                       device_name=self.device_name,
                                       device_loc=self.device_location)
        self._device_settings.start_time = arrow.now()

    def _get_device_links(self):
        if self._device_settings.device_url is not None:
            get_url = self._device_settings.device_url
            link_response = get(url=get_url)
            if link_response.status_code == 200:
                collection = Collection.from_json(link_response.text)
                device_id = [data.value for data in collection.items[0].data if data.name == 'device_id'][0]
                if device_id is not None:
                    self._device_settings.device_id = device_id
                for link in collection.links:
                    if link.rel == 'latest':
                        self._device_settings.latest_url = link.href
                    else:
                        resp = get(url=link.href)
                        if resp.status_code == 200:
                            link_coll = Collection.from_json(resp.text)
                            self._device_settings.process_measurement_template(link_coll, link.rel)

    def _setup_device(self):
        self._init_settings()
        self._register_device()
        self._get_device_links()

    def start_client(self):
        if self.simulate_sensor is True:
            from stemlab_client.sensors.dht22_sensor_simulator import DHT22Sensor
        else:
            from stemlab_client.sensors.dht22_sensor import DHT22Sensor

        try:
            exit_monitor = GracefulExit()
            self._load_persistent_data()
            if self._device_settings is None:
                self._setup_device()
                shelve_db = shelve.open(self._db_filename, writeback=True)
                shelve_db[self.SETTINGS_KEY] = self._device_settings
                shelve_db.close()

            sensor = DHT22Sensor(self._device_settings.device_id,
                                 units=FAHRENHEIT)
            executor = ThreadPoolExecutor(4)
            next_reading = time.time()

            while True:
                readings = sensor.poll()
                for reading in readings:
                    template = self._device_settings.measurement_templates[reading.measurement_type.name]
                    post_data = generate_measurement_params(template, reading)
                    post_future = executor.submit(post, post_data['href'], post_data['params'])
                    post_future.add_done_callback(callback_reading_post)
                next_reading += self.poll_interval
                time.sleep(next_reading - time.time())
                if exit_monitor.exit_now is True:
                    break

        except Exception as e:
            print traceback.format_exc()
            print str(e)

def main(api_host,
         poll_interval,
         **kwargs):
    client = SensorClient(api_host=api_host,
                          poll_interval=poll_interval,
                          **kwargs)

    client.start_client()
    print "Shutting down"


def launch():
    argparser = argparse.ArgumentParser(
            description="""
Sensor client module that provides command and control for sensor read and report functions.
Initializes the sensor device, registers with remote server and provides data persistence
""",
            formatter_class=argparse.RawDescriptionHelpFormatter
            )
    argparser.add_argument('--api_host', help='''API server address this device will connect and register.
     Valid ip address or resolvable hostname.
        ''',
                           required=True)
    argparser.add_argument('--poll_interval',
                           help='''In seconds, the interval between sensor polls. This interval applies to all sensors
                                Minimum interval value is 5 seconds''',
                           required=True)
    argparser.add_argument('--api_port',
                           help='Port to use to connect to API server. Default is 80',
                           required=False)
    argparser.add_argument('--device_name',
                           help='''Name to register this device under with remote API server. Name must be unique.
                            Defaults to device hostname.''',
                           required=False)
    argparser.add_argument('--device_loc',
                           help='A physical location for the device. May be description, lat/long, etc.',
                           required=False)
    argparser.add_argument('-u','--username',
                           help='Username for API authentication if authentication is supported.',
                           required=False)
    argparser.add_argument('-p','--password',
                           help='Password for API authentication if authentication is supported. Required if username set.',
                           required=False)
    argparser.add_argument('--sim_sensor', action='store_true',
                           help='Pass this parameter to utilize a sensor simulator instead of actual sensor',
                           required=False)
    args = argparser.parse_args()

    api_host = args.api_host
    poll_interval = args.poll_interval
    kwargs = {}
    if args.api_port:
        kwargs['api_port'] = args.api_port

    if args.device_name:
        kwargs['device_name'] = args.device_name

    if args.device_loc:
        kwargs['device_loc'] = args.device_loc

    if args.username:
        kwargs['username'] = args.username

    if args.password:
        kwargs['password'] = args.password
    else:
        if args.username:
            raise ValueError("Password required when passing Username")

    if args.sim_sensor:
        kwargs['sim_sensor'] = True

    main(api_host, poll_interval, **kwargs)

if __name__ == "__main__":
    launch()
