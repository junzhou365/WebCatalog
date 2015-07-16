from flask import Blueprint
catalog = Blueprint('catalog', __name__, template_folder='templates', static_folder='static')

from . import catalogViews, catalog_models
