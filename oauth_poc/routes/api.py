from flask import Blueprint, request, make_response, jsonify
import json

from utils import session_data, decode_base64, get_user

api_bp = Blueprint('api_bp', __name__)

# Route: Mock API Route


@api_bp.route('/api', methods=['GET'])
def api():
    session_id = request.cookies.get('session_id')
    user_data = session_data.get(session_id)
    if not user_data:
        data = {
            "error": 'User is not authenticated',
        }
        return make_response(jsonify(data), 401)

    data = {
        "data": f"some very important data for a user {get_user(session_id).get('name')}",
    }
    return make_response(jsonify(data), 200)

# User Info Route (not used in the frontend)


@api_bp.route('/userinfo', methods=['GET'])
def userinfo():
    session_id = request.cookies.get('session_id')
    user_data = session_data.get(session_id)
    if not user_data:
        data = {
            "error": 'User is not authenticated',
        }
        return make_response(jsonify(data), 401)

    id_token = user_data.get('id_token')
    
    # for educational purposes only
    payload_decoded = decode_base64(id_token.split('.')[1])
    name = json.loads(payload_decoded).get('name')
    email = json.loads(payload_decoded).get('email')
    data = {
        'name': name,
        'email': email
    }
    return make_response(jsonify(data), 200)
