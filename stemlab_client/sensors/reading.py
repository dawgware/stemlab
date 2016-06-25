"""
    Created: June 21, 2016
    Author: Carl Wilen

    A Reading contains a measurement collected at a point in time from a Sensor. Readings consist of a measurement
    value, timestamp and a measurement type.

"""
from arrow import Arrow
import arrow

class Reading(object):

    def __init__(self, device_id, measurement, timestamp, measurement_type):

        if device_id is None:
            raise ValueError("Reading requires a device_id.")

        if measurement is None:
            raise ValueError("Reading requires a measurement.")

        if timestamp is None:
            raise ValueError("Reading requires a timestamp")

        if measurement_type is None:
            raise ValueError("A measurement_type is required")

        self._measurement = measurement
        self._timestamp = timestamp
        self._measurement_type = measurement_type
        self._device_id = device_id

    @property
    def device_id(self):
        return self._device_id

    @property
    def measurement(self):
        return self._measurement

    @property
    def measurement_type(self):
        return self._measurement_type

    @property
    def timestamp(self):
        return str(arrow.get(self._timestamp).to('local'))

    def get_timestamp_(self):
        return self._timestamp

