import unittest
from stemlab_client.sensors.dht22_sensor import DHT22Sensor


class DHT22SensorTestCase(unittest.TestCase):

    def test_poll(self):
        sensor = DHT22Sensor()
        test_readings = sensor.poll()
        for reading in test_readings:
            print reading.measurement_type.unit
            print reading.measurement
            print reading.timestamp

if __name__ == '__main__':
    unittest.main()
