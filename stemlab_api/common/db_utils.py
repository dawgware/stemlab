from influxdb import InfluxDBClient
from stemlab_api.common.utils import hasitems


client = None

TEMPERATURE='temperature'
HUMIDITY='humidity'
DB_NAME='device_readings'


class DBUtils(object):

    def __init__(self):
        self.client = None

    def db_connect(self, host, username=None, password=None, database=None, port=8086):
        # self.client = InfluxDBClient(host=host,
        #                         port=port,
        #                         username=username,
        #                         password=password,
        #                         database=database)
        print "CONNECTING TO INFLUXDB"
        if database is not None:
            self.client = InfluxDBClient(host=host,
                                         database=database)
        else:
            self.client = InfluxDBClient(host=host)

        print "CONNECTING"

    def db_close(self):
        del self.client

    def insert_reading(self, data_record):
        try:
            if self.client is not None:
                self.client.write_points(points=data_record,
                                         time_precision="s")
        except Exception as e:
            raise e

    def get_reading_by_device_time(self, device_id, timestamp, measurement=None):
        result = None
        if device_id is not None and timestamp is not None:
            filters = [{'field': 'device_id',
                        'value': device_id,
                        'operator': '='},
                       {'field': 'time',
                        'operator': '=',
                        'value': timestamp}]
            result = self.get_reading(filters, measurement)
        return result

    def create_database(self, db_name):
        self.client.create_database(db_name, if_not_exists=True)

    def drop_database(self, db_name):
        self.client.drop_database(db_name)

    def get_device_humidity_readings(self, device_id):
        return self.get_device_readings(device_id, measurement=HUMIDITY)

    def get_device_temperature_readings(self, device_id):
        return self.get_device_readings(device_id, TEMPERATURE)

    def get_reading_by_log_id(self, log_id, measurement):
        result = None
        if log_id is not None:
            filters = [{'field': 'log_id',
                        'value': log_id,
                        'operator': '='}]
            result = self.get_reading(filters, measurement)
            print "RESULTS: ", result
        return result

    def get_device_readings(self, device_id, measurement=TEMPERATURE):
        result = None
        if device_id is not None:
            filters = [{'field': 'device_id',
                        'value': device_id,
                        'operator': '='}]
            result = self.get_reading(filters, measurement)
        return result

    def get_reading_with_sql(self, query, measurement=None):
        """
        Get points using a prepared query. If the prepared query is mal-formed an Exception is thrown.
        :param query:  the prepared query to call against readings database.
        :param measurement: TEMPERATURE or HUMIDITY
        :return:  ResultQuery or None if no data found.
        """
        result = None
        if query is not None:
            result = self.client.query(query=query)

        return result

    def get_reading(self, filters, measurement=None, fields=None):
        mask = '{field} {oper} {val}'
        str_mask = "{field} {oper} '{val}'"
        conditions = []
        select = ""
        if hasitems(filters):
            for filter in filters:
                field = filter['field']
                oper = filter['operator']
                val = filter['value']
                use_mask = str_mask if isinstance(val, str) or isinstance(val, unicode) else mask
                if filter['field'] == 'time':
                    # val = str(val) + "s"
                    val = str(val)

                conditions.append(use_mask.format(field=field,
                                                  oper=oper,
                                                  val=val))

        if hasitems(fields) and isinstance(fields, list):
            select = "SELECT " + ','.join(fields)
        else:
            select = "SELECT * "

        if measurement is not None:
            select += " FROM " + measurement
        else:
            select += " FROM {t},{h}".format(t=TEMPERATURE, h=HUMIDITY)

        if hasitems(conditions):
            select += " WHERE " + " and ".join(conditions) + ";"

        result = self.client.query(query=select)
        return result

