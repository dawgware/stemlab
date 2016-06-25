from flask_sqlalchemy import SQLAlchemy
from stemlab_api.apimarshmallow import ApiMarshmallow
from stemlab_api.common.db_utils import DBUtils

db_client = DBUtils()
ma = ApiMarshmallow()
db = SQLAlchemy()

