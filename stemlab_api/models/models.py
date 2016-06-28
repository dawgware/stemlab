from flask import url_for
from stemlab_api.database import db
from stemlab_api.common.db_utils import TEMPERATURE, HUMIDITY

class Devices(db.Model):
    device_id = db.Column(db.String(36), primary_key=True)
    device_name = db.Column(db.String(50))
    location = db.Column(db.String(100))
    temperature_sensor = db.Column(db.Boolean)
    humidity_sensor = db.Column(db.Boolean)
    uptime = db.Column(db.BigInteger)

    @property
    def url(self):
        return url_for('DevicesView:get', device_id=self.device_id,  _external=True)

class Readings(object):

    def __init__(self, timestamp, device_id, units, log_id=None, device_name=None, location=None):
        self._log_id = log_id
        self._timestamp = timestamp
        self._device_id = device_id
        self._device_name = device_name
        self._location = location
        self._units = units


    @property
    def log_id(self):
        return self._log_id

    @log_id.setter
    def log_id(self, value):
        self._log_id = value

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        self._device_id = value

    @property
    def device_name(self):
        return self._device_name

    @device_name.setter
    def device_name(self, value):
        self._device_id = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, value):
        self._units = value

    @property
    def timestamp(self):
        return self._timestamp


class TemperatureReadings(Readings):

    def __init__(self, timestamp, temperature, device_id, units, log_id=None, device_name=None, location=None):

        super(TemperatureReadings, self).__init__(log_id=log_id,
                                                  device_id=device_id,
                                                  units=units,
                                                  timestamp=timestamp,
                                                  device_name=device_name,
                                                  location=location)
        self._temperature = temperature

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @property
    def url(self):
        return url_for('TemperatureReadingsView:get', log_id=self.log_id,  _external=True)

    def db_record(self):
        record = [
            {
                "measurement": "temperature",
                "tags": {
                    "device_id": self.device_id,
                    "device_name": self.device_name,
                    "location": self.location,
                    "units": self.units,
                    "log_id": self.log_id
                },
                "time": self.timestamp,
                "fields": {
                    "value": self.temperature
                }
            }
        ]
        return record


class HumidityReadings(Readings):
    def __init__(self, timestamp, humidity, device_id, units, log_id=None, device_name=None, location=None):

        super(HumidityReadings, self).__init__(log_id=log_id,
                                               device_id=device_id,
                                               units=units,
                                               timestamp=timestamp,
                                               device_name=device_name,
                                               location=location)
        self._humidity = humidity

    @property
    def humidity(self):
        return self._humidity

    @humidity.setter
    def humidity(self, value):
        self._humidity = value

    @property
    def url(self):
        return url_for('HumidityReadingsView:get', log_id=self.log_id,  _external=True)

    def db_record(self):
        record = [
            {
                "measurement": "humidity",
                "tags": {
                    "device_id": self.device_id,
                    "device_name": self.device_name,
                    "location": self.location,
                    "units": self.units,
                    "log_id": self.log_id

                },
                "time": self.timestamp,
                "fields": {
                    "value": self.humidity
                }
            }
        ]
        return record


def reading_factory(timestamp, device_id, units, device_name, location, log_id, value, measurement):
    if measurement == TEMPERATURE:
        return TemperatureReadings(temperature=value,
                                   timestamp=timestamp,
                                   device_id=device_id,
                                   device_name=device_name,
                                   location=location,
                                   units=units,
                                   log_id=log_id)
    elif measurement == HUMIDITY:
        return HumidityReadings(humidity=value,
                                timestamp=timestamp,
                                device_id=device_id,
                                device_name=device_name,
                                location=location,
                                units=units,
                                log_id=log_id)
    else:
        return None