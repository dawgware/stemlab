"""
    Created: June 22, 2016
    Author: Carl Wilen

    Lists the various measurement types that can be returned by various Sensors.

"""

PERCENTAGE = 'Percentage'
CELSIUS = 'Celsius'
FAHRENHEIT = 'Fahrenheit'
KELVIN = 'Kelvin'

class MeasurementType(object):

    _description = ''
    _name = ''
    _unitsofmeasure = ''

    def __init__(self, units):
        if units is None:
            raise ValueError("A units needs to be specified for the type")
        self._units = units

    @property
    def description(self):
        """
        Description of measurement type
        :return: String
        """
        return self._description

    @property
    def name(self):
        """
        A short name for the measurement type
        :return: String name.
        """
        return self._name

    @property
    def unitsofmeasure(self):
        """
        List of the valid units of measure for this type.
        :return: List
        """
        return self._unitsofmeasure

    @property
    def units(self):
        """
        Unit of measurment for this type. Defined and specific to the type itself.
        :return: The type's units
        """
        return self._units

    @units.setter
    def units(self, value):
        if value is None:
            raise ValueError("A units value was not specified")
        self._units = value


class TemperatureMeasurementType(MeasurementType):

    _description = '''An objective comparative measure of hot or cold. Reported in units of either Celcius,
                    Fahrenheit, or Kelvin.'''
    _name = 'temperature'
    _unitsofmeasure = [CELSIUS, FAHRENHEIT, KELVIN]

    def __init__(self, units=CELSIUS, scale=None):
        if units not in self._unitsofmeasure:
            raise ValueError("The units {u} is not a valid temperature units".format(u=unit))

        super(TemperatureMeasurementType, self).__init__(units=units)

    @staticmethod
    def celsius_to_fahrenheit(temperature):
        if temperature is not None:
            return (temperature * 1.8) + 32
        return temperature

    @staticmethod
    def fahrenheit_to_celsius(temperature):
        if temperature is not None:
            return (temperature - 32) * (float(5)/float(9))
        return temperature


class HumidityMeasurementType(MeasurementType):

    _description = '''A measure of the relative measure of the amount of water vapor in the air.'''
    _name = 'humidity'
    _unitsofmeasure = [PERCENTAGE]

    def __init__(self, units=PERCENTAGE, scale=None):
        if units not in self._unitsofmeasure:
            raise ValueError("The units {u} is not a valid humidity units".format(u=units))
        super(HumidityMeasurementType, self).__init__(units)

