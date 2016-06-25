"""
    Created: June 22, 2016
    Author: Carl Wilen

    Stores information about the device hosting the sensors.
"""
import socket
from arrow import Arrow
import arrow


class Device(object):

    _api_port = None
    _device_id = None
    _start_time = None
    _latest_url = None

    def __init__(self, api_host,
                 api_port,
                 device_name=None,
                 device_loc=None):
        self._api_port = api_port
        self._api_host = api_host
        self._device_name = device_name
        self._device_loc = device_loc
        self._measurement_templates = {}
        self._device_url = None
        if self._device_name is None:
            self._device_name = socket.gethostname()

    def __repr__(self):
        ret = '''
        Device_name: {n}
        Device_id: {id}
        Device_loc: {loc}
        Device Url: {url}
        Start Time: {st}
        Timezone: {tz}
        TZ Offset: {offset}
        Uptime: {up}
        API Host: {host}
        API Port: {port}
        Measurements: {meas}
        '''.format(n=self.device_name,
                   id=self.device_id,
                   loc=self.device_loc,
                   st=self.start_time,
                   tz=self.timezone,
                   offset=self.tz_offset,
                   host=self.api_host,
                   port=self.api_port,
                   up=self.uptime(),
                   url=self.device_url,
                   meas=self._measurement_templates.keys())
        return ret

    @property
    def latest_url(self):
        return self._latest_url

    @latest_url.setter
    def latest_url(self, url):
        if url is not None:
            self._latest_url = url

    @property
    def device_url(self):
        return self._device_url

    @device_url.setter
    def device_url(self, url):
        if url is not None:
            self._device_url = url

    @property
    def device_name(self):
        return self._device_name

    @property
    def device_loc(self):
        return self._device_loc

    @property
    def api_port(self):
        return self._api_port

    @property
    def api_host(self):
        return self._api_host

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        if value is not None:
            self._device_id = value

    @device_loc.setter
    def device_loc(self, value):
        if value is not None:
            self._device_loc = value

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        if value is not None and isinstance(value, Arrow):
            self._start_time = value

    @property
    def timezone(self):
        return self._start_time.tzname()

    @property
    def tz_offset(self):
        return self._start_time.utcoffset().total_seconds()/3600

    @property
    def measurement_templates(self):
        return self._measurement_templates

    def uptime(self):
        return int((arrow.now() - self._start_time).total_seconds())

    def process_measurement_template(self, template_data, measurement):
        if template_data is not None and measurement is not None:
            m_template = {}
            m_template['href'] = template_data.href
            data = template_data.template.data
            m_template['param_names'] = [item.name for item in data]
            self._measurement_templates[measurement] = m_template


