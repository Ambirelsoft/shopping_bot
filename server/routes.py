from flask import Blueprint
from flask import request
from server.handlers import process_data

api = Blueprint('api', __name__)


@api.route('/', methods=['POST'])
def order_products():
    data = request.get_json()
    response = process_data(data)
    return str(response)
