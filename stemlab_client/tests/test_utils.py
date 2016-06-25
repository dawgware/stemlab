import unittest
from stemlab_client.common.utils import generate_measurement_params
from stemlab_client.common.measurement_types import TemperatureMeasurementType
from stemlab_client.sensors.reading import Reading
from arrow import Arrow
import arrow

class UtilsTestCase(unittest.TestCase):

    def test_generate_measurement_types(self):
        test_type = TemperatureMeasurementType()
        test_reading = Reading(device_id='b7a77117-533b-4c4a-be31-c621cd3c2f25',
                               measurement=99.9,
                               timestamp=arrow.now('local').timestamp,
                               measurement_type=test_type)
        template = {'href':'http://localhost:5000/readings/temperature/',
                    'param_names': ['timestamp', 'measurement', 'device_id']}
        test_dict = generate_measurement_params(template=template,
                                                reading=test_reading)
        print test_dict

if __name__ == '__main__':
    unittest.main()
