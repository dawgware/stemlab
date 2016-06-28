from stemlab_api import app
from stemlab_api.database import db, ma, db_client
from os import path as op
from path import Path
from stemlab_api.models.models import Devices, Readings
import traceback
import argparse

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


def setup_databases(influx_host):

    current_db = Path.joinpath(app.config['DATA_DIRECTORY'],'stemlab_api.db')
    if not current_db.exists():
        with app.app_context():
            db.create_all()

    ##
    # Init the InfluxDB connection
    ##
    db_client.db_connect(host=influx_host, database='device_readings')

def launch():
    argparser = argparse.ArgumentParser(
            description="""
Sensor REST API module that provides sensor reading data storage and retrieval
""",
            formatter_class=argparse.RawDescriptionHelpFormatter
            )
    argparser.add_argument('--influx_host', help='''Ip Address or hostname for server hosting InfluxDB instance. Requires
      a valid ip address or resolvable hostname.
        ''',
                           required=True)
    argparser.add_argument('--debug', action='store_true',
                           help='Run this API in debug mode',
                           required=False)
    args = argparser.parse_args()
    influx_host = args.influx_host
    debug = False
    if args.debug:
        debug = args.debug
    try:
        # app = create_app()
        # setup_databases(app)
        # init_views(app)
        create_app()
        setup_databases(influx_host=influx_host)
        init_views()
        if not debug:
            app.run(host='0.0.0.0')
        else:
            app.run(debug=True)
    except Exception as e:
        print traceback.format_exc()

if __name__ == '__main__':
    print "INSIDE MAIN"
    launch()
