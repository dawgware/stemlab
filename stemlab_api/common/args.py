from webargs import fields, validate

device_args = {

    # Required arguments
    'device_name': fields.Str(required=True),

    'location': fields.Str(),

    # Default value when argument is missing
    'temperature_sensor': fields.Boolean(missing=False),
    'humidity_sensor': fields.Boolean(missing=False),
    'uptime': fields.Int()

}

device_name_args = {
    'device_name': fields.Str(required=True)
}

temperature_reading_args = {
    'device_id': fields.Str(required=True),
    'temperature': fields.Decimal(required=True),
    'timestamp': fields.String(required=True)
}

humidity_reading_args = {
    'device_id': fields.Str(required=True),
    'humidity': fields.Decimal(required=True),
    'timestamp': fields.String(required=True)
}

reading_args = {
    'device_id': fields.Str(required=True),
    'measurement': fields.Decimal(required=True),
    'timestamp': fields.String(required=True)
}
