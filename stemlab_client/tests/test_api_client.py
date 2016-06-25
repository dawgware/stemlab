import unittest
from collection_json import Collection
from stemlab_client.api_client import get, post
import requests
from requests import ConnectTimeout
from stemlab_client.sensors.dht22_sensor_simulator import DHT22Sensor
from stemlab_client.common.utils import generate_measurement_params


class Api_ClientTestCase(unittest.TestCase):

    def setUp(self):
        self.test_url = "http://localhost:5000"
        self.test_device_name = "TEST_CASE_DEVICE_NAME"

    def tearDown(self):
        try:
            params = {'device_name': self.test_device_name}
            response = requests.delete(self.test_url + '/devices/', params=params, timeout=5)
        except Exception as e:
            pass

    def test_get(self):
        test_url = self.test_url + "/devices/7324ef5a-b1a6-4ff4-9d97-61b4dde35924"
        test_response = get(test_url)
        collection = Collection.from_json(test_response.text)
        print collection.version
        print collection.href
        print [data.name for data in collection.items[0].data]
        device_id = [data.value for data in collection.items[0].data if data.name == 'device_id']
        print "DEVICE: ", device_id

    def test_get_bad_host(self):
        test_url = "http://172.1.1.1:5000/devices/7324ef5a-b1a6-4ff4-9d97-61b4dde35924"
        with self.assertRaises(ConnectTimeout) as context:
            test_response = get(test_url)
        self.assertEqual(ConnectTimeout, context.exception.__class__,  """
        Api_ClientTestCase::test_get_bad_host:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected='ConnectTimeout', returned=context.exception.__class__))

    def test_get_by_date_device(self):
        test_url = self.test_url + "/devices/0c89fded-76ea-4890-a8a1-25c25b24986d/2013-06-13T13:49:23-04:00"
        test_response = get(test_url)
        collection = Collection.from_json(test_response.text)
        self.assertIsNotNone(collection.items, """
        Api_ClientTestCase::test_get_by_date_device:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected='values', returned='None'))

    def test_post_device(self):
        test_url = self.test_url + "/devices/"
        data = {'device_name': self.test_device_name,
                'humidity_sensor': 'true',
                'temperature_sensor': 'true',
                'location': 'lwr05_lab'}
        test_response = post(test_url, data=data)
        self.assertTrue(test_response.status_code == 200,  """
        Api_ClientTestCase::test_post_device:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=200, returned=test_response.status_code))

    def test_get_template(self):
        test_url = self.test_url + "/readings/temperature/template/7324ef5a-b1a6-4ff4-9d97-61b4dde35924"
        test_response = get(test_url)
        collection = Collection.from_json(test_response.text)
        print collection.version
        print collection.href
        data = collection.template.data
        print [item.name for item in data]

    def test_post_temperature_reading(self):
        test_url = self.test_url + "/readings/temperature/"
        templates = {'humidity': {'href':'http://localhost:5000/readings/humidity/',
                    'param_names': ['timestamp', 'measurement', 'device_id']},
                     'temperature': {'href':'http://localhost:5000/readings/temperature/',
                     'param_names': ['timestamp', 'measurement', 'device_id']}}

        test_readings = DHT22Sensor('b7a77117-533b-4c4a-be31-c621cd3c2f25').poll()
        for reading in test_readings:
            post_data = generate_measurement_params(templates[reading.measurement_type.name], reading)
            test_response = post(post_data['href'], data=post_data['params'])
            self.assertTrue(test_response.status_code == 200,  """
            Api_ClientTestCase::test_post_temperature_reading:
            Expected '{expected}' got '{returned}' value instead
            """.format(expected='Status 200', returned=test_response.status_code))

if __name__ == '__main__':
    unittest.main()
