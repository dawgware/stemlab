import unittest
from stemlab_api.common.db_utils import DBUtils
from stemlab_api.models.models import TemperatureReadings, HumidityReadings
from influxdb.resultset import ResultSet

import uuid
import arrow
import random
from arrow import Arrow


class DBUtilsTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


    def setUp(self):
        self.db_client = DBUtils()
        self.db_name = 'test_readings'
        self.db_client.db_connect(host='localhost', database=self.db_name)
        self.db_client.create_database(self.db_name)
        self.test_temp_readings = []
        self.test_humid_readings = []
        self.current_time = arrow.now()
        self.loadup(num_devices=10)

    def loadup(self, num_cycles=5, time_interval='day', num_devices=2):
        devices = []
        for n in range(0, num_devices):
            device = {}
            device_id='0c89fded-76ea-4890-a8a1-25c25b24{id}'.format(id=hex(random.randint(10000,99999))[2:6])
            device['device_id'] = device_id
            devices.append(device)
        for i in range(0,num_cycles):
            timestamp = 0
            if time_interval == 'min':
                timestamp=str(self.current_time.replace(minute=self.current_time.minute - i))
            elif time_interval == 'hour':
                timestamp=str(self.current_time.replace(hour=self.current_time.hour - i))
            else:
                timestamp=str(self.current_time.replace(day=self.current_time.day - i))
            for device in devices:
                log_id='29e8ae64-ae9d-4e70-970c-2ed30cc9{id}'.format(id=hex(random.randint(10000,99999))[2:6])
                temp = round(random.uniform(65.4,95.6),2)
                humid = round(random.uniform(25.3,84.9),2)
                temp_reading = TemperatureReadings(temperature=temp,
                                   timestamp=str(self.current_time.replace(day=self.current_time.day - i)),
                                   device_id=device['device_id'],
                                   log_id=log_id)
                humid_reading = HumidityReadings(humidity=humid,
                                              timestamp=str(self.current_time.replace(day=self.current_time.day - i)),
                                              device_id=device['device_id'],
                                              log_id=log_id)
                self.db_client.insert_reading(temp_reading.db_record())
                self.db_client.insert_reading(humid_reading.db_record())
                self.test_temp_readings.append(temp_reading)
                self.test_humid_readings.append(humid_reading)

    def doCleanups(self):
        self.db_client.drop_database(self.db_name)
        self.db_client.db_close()

    def test_get_device_readings(self):
        test_device_id = self.test_temp_readings[0].device_id
        test_log_id = self.test_temp_readings[0].log_id
        test_result = self.db_client.get_device_readings(test_device_id)
        result_list = list(test_result.get_points(measurement='temperature'))
        self.assertTrue(len(result_list) > 0,  """
        DBUtilsTestCase::test_get_device_readings:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=1, returned=len(result_list)))
        result_device_id = result_list[0]['device_id']
        result_log_id = result_list[0]['log_id']
        self.assertEqual(test_device_id, result_device_id,  """
        DBUtilsTestCase::test_get_device_readings:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=test_device_id, returned=result_device_id))
        self.assertEqual(test_log_id, result_log_id,  """
        DBUtilsTestCase::test_get_device_readings:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=test_log_id, returned=result_log_id))

    def test_get_reading_by_device_time(self):
        test_device_id = self.test_temp_readings[0].device_id
        test_time = arrow.get(self.test_temp_readings[0].timestamp)
        # test_timestamp = test_time.timestamp*1000000000
        test_timestamp = test_time.timestamp
        results = self.db_client.get_reading_by_device_time(test_device_id, test_timestamp)
        result_list = list(results.get_points(measurement='temperature'))
        result_device_id = result_list[0]['device_id']
        result_timestamp = arrow.get(result_list[0]['time']).timestamp
        self.assertTrue(len(result_list) > 0,  """
        DBUtilsTestCase::test_get_reading_by_device_time:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=1, returned=len(result_list)))
        self.assertEqual(test_device_id, result_device_id,  """
        DBUtilsTestCase::test_get_reading_by_device_time:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=test_device_id, returned=result_device_id))
        self.assertEqual(test_time.timestamp, result_timestamp,  """
        DBUtilsTestCase::test_get_reading_by_device_time:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=test_time.timestamp, returned=result_timestamp))

    def test_get_reading_by_log_id(self):
        test_log_id = self.test_temp_readings[0].log_id
        results = self.db_client.get_reading_by_log_id(test_log_id, 'temperature')
        result_list = list(results.get_points(measurement='temperature'))
        result_log_id = result_list[0]['log_id']
        self.assertTrue(len(result_list)>0,  """
        DBUtilsTestCase::test_get_reading_by_log_id:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected='>0', returned='0'))
        self.assertEqual(result_log_id, test_log_id,  """
        DBUtilsTestCase::test_get_reading_by_log_id:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=test_log_id, returned=result_log_id))

        results = None
        result_list = []
        results = self.db_client.get_reading_by_log_id(test_log_id, 'humidity')
        result_list = list(results.get_points(measurement='humidity'))
        result_log_id = result_list[0]['log_id']
        self.assertTrue(len(result_list)>0,  """
        DBUtilsTestCase::test_get_reading_by_log_id:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected='>0', returned='0'))
        self.assertEqual(result_log_id, test_log_id,  """
        DBUtilsTestCase::test_get_reading_by_log_id:
        Expected '{expected}' got '{returned}' value instead
        """.format(expected=test_log_id, returned=result_log_id))

if __name__ == '__main__':
    unittest.main()
