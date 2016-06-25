import unittest
from stemlab_client.sensor_client import SensorClient
from path import Path
import requests


class SensorClientTestCase(unittest.TestCase):

    def setUp(self):
        self.db_file = Path('test_shelve.db')
        self.db_file.remove_p()
        self.test_device_name = 'TEST_CASE_DEVICE'
        self.test_params = {'device_name': self.test_device_name,
                            'device_loc': 'test_case_loc',
                            'api_port': 5000}
        self.test_devices_url = 'http://localhost:5000/devices/'
        self.test_api_host = 'localhost'

    def tearDown(self):
        try:
            params = {'device_name': self.test_device_name}
            response = requests.delete(self.test_devices_url, params=params, timeout=5)
        except Exception as e:
            pass

    def test_init_settings(self):
        test_client = SensorClient(self.test_api_host, 900, **self.test_params)

        test_client._init_settings()
        print test_client._device_settings

    def test_register_device(self):
        test_client = SensorClient(self.test_api_host, 900, **self.test_params)
        test_client._init_settings()
        test_client._register_device()
        self.assertIsNotNone(test_client._device_settings.device_url,  """
        SensorClientTestCase::test_register_device:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected='Registered device with url.', returned='Device not registered'))

    def test_get_device_links(self):
        test_client = SensorClient(self.test_api_host, 900, **self.test_params)
        test_client._init_settings()
        test_client._register_device()
        test_client._get_device_links()
        print test_client._device_settings
        templates = test_client._device_settings.measurement_templates
        for key, template in templates.items():
            print key, template

    def test_start_client(self):
        test_client = SensorClient(self.test_api_host, 10, **self.test_params)
        test_client.start_client()

if __name__ == '__main__':
    unittest.main()
