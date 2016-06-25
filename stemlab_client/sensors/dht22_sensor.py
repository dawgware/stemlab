"""
    Created: June 22, 2016
    Author: Carl Wilen

    Sensor implementation for the DHT22 temperature and humidity sensor. This sensor provides both temperature and humidity
    measurements. Poll intervals must be greater than 2 seconds to avoid failures.
"""
import arrow
import random
import time
from stemlab_client.sensors.sensor import Sensor
from stemlab_client.common.measurement_types import TemperatureMeasurementType, HumidityMeasurementType
from stemlab_client.common.measurement_types import CELSIUS, FAHRENHEIT, KELVIN, PERCENTAGE
from stemlab_client.sensors.reading import Reading


class DHT22Sensor(Sensor):

    _measurement_types = {'temperature': TemperatureMeasurementType(),
                          'humidity': HumidityMeasurementType()}

    def __init__(self, device_id, unit=CELSIUS, gpio_pin=4):

        super(DHT22Sensor, self).__init__(device_id)

        self.default_unit = unit
        self.sensor_type = 22
        self.gpio_pin = gpio_pin
        if unit == FAHRENHEIT:
            self.fahrenheit = True
        self._measurement_types['temperature'].unit = self.default_unit

    def poll(self):
        """
        Poll the DHT22 for temperature and humidity measurements.
        :return: List of Readings for Temperature and Humidity
        """
        readings = []
        try:
            timestamp = arrow.now()
            time.sleep(random.randint(0,5))
            temperature = round(random.uniform(65.4, 95.6), 2)
            if self.default_unit == CELSIUS:
                temperature = round(TemperatureMeasurementType.fahrenheit_to_celsius(temperature), 2)
            humidity = round(random.uniform(25.3, 84.9), 2)
            readings.append(Reading(device_id=self._device_id,
                                    measurement=temperature,
                                    timestamp=timestamp,
                                    measurement_type=self._measurement_types['temperature']))
            readings.append(Reading(device_id=self._device_id,
                                    measurement=humidity,
                                    timestamp=timestamp,
                                    measurement_type=self._measurement_types['humidity']))
        except Exception as e:
            raise e
        return readings



