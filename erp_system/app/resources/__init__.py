from flask import Blueprint

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')

from . import routes