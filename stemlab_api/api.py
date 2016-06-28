from stemlab_api import app
from stemlab_api.database import db, ma, db_client
from os import path as op
from path import Path
from stemlab_api.models.models import Devices, Readings
import traceback

__version__ = 1.0
__author__ = "dawgwaredev@gmail.com"


def create_app():
    # app = Flask(__name__)
    # api_bp = Blueprint('api',__name__)
    app.config['DATA_DIRECTORY'] = app.root_path
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(op.join(app.config['DATA_DIRECTORY'],'stemlab_api.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # return app


def init_views():
    ma.make_smore(app)
    from stemlab_api.resources.device import DevicesView
    from stemlab_api.resources.readings import TemperatureReadingsView, HumidityReadingsView
    DevicesView.register(app)
    TemperatureReadingsView.register(app)
    HumidityReadingsView.register(app)


def setup_databases():

    current_db = Path.joinpath(app.config['DATA_DIRECTORY'],'stemlab_api.db')
    if not current_db.exists():
        with app.app_context():
            db.create_all()
            import uuid
            # device = Devices(device_id=str(uuid.uuid4()), device_name='raspi001', location='LWR05.1.219',
            #                  temperature_sensor=True,
            #                  humidity_sensor=True,
            #                  uptime=1)
            # db.session.add(device)
            # device = Devices(device_id=str(uuid.uuid4()), device_name='raspi002', location='LWR05.1.210',
            #                  temperature_sensor=True,
            #                  humidity_sensor=True,
            #                  uptime=1)
            # db.session.add(device)
            # db.session.commit()
    ##
    # Init the InfluxDB connection
    ##
    db_client.db_connect(host='localhost', database='device_readings')
    # db_client.db_connect(host='localhost')
    # db_client.create_database('device_readings')


if __name__ == '__main__':
    print "INSIDE MAIN"
    try:
        # app = create_app()
        # setup_databases(app)
        # init_views(app)
        create_app()
        setup_databases()
        init_views()
        app.run(debug=True)
    except Exception as e:
       print traceback.format_exc()
