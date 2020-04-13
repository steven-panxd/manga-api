from . import api_mask
from app.utils.response import PageNotFound


@api_mask.route('/', methods=['GET'])
def index():
    return PageNotFound()
