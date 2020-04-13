from flask import Blueprint

api_mask = Blueprint('api_mask', __name__)

from . import mask
