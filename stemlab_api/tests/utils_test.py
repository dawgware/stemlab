import unittest
from stemlab_api.common.utils import create_url_with_params
import urllib

class UtilsTestCase(unittest.TestCase):

    def test_create_url(self):
        base_url = "http://localhost:5000/temperaturereadings"
        params = {'log_id':'29e8ae64-ae9d-4e70-970c-2ed30cc9a9e5', 'device_id':'29e8ae64-ae9d-4e70-970c-2ed30cc9a2342'}
        test_url = create_url_with_params(base_url, params)
        print test_url
        params = {'log_id':'29e8ae64-ae9d-4e70-970c-2ed30cc9a9e5'}
        test_url = create_url_with_params(base_url, params)
        print test_url

    def test_create_url_bad_params(self):
        base_url = "http://localhost:5000/temperaturereadings"
        params = {'log_id':''}
        test_url = create_url_with_params(base_url, params)
        print test_url


if __name__ == '__main__':
    unittest.main()
