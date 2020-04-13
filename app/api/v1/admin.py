from app.api.v1 import api_v1


@api_v1.route('/admin/add_slide', methods=['POST'])
def add_slide():
    return 'add_slide'
