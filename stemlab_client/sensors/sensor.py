"""
    Created: June 21, 2016
    Author: Carl Wilen

    A sensor collects data about events or changes in its environment. The data is in the form of a measurement. A
    sensor may provide more than one type of measurement. To get the sensor's measurement one has to poll the sensor.
    When polled the sensor returns its current measurement value(s). Measurements are collected in a point in time.
    A measurement, timestamp and type of measurement create a reading. Readings are returned when a Sensor implementation
    is polled.

"""


class Sensor(object):

    _measurement_types = None

    def __init__(self, device_id):
        self._device_id = device_id

    @property
    def measurement_types(self):
        return self._measurement_types
    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        if value is not None:
            self._device_id = value

    def poll(self):
        """
        Method to capture the sensors current measurement value(s)
        :return: List of Readings
        """
        raise NotImplementedError()



