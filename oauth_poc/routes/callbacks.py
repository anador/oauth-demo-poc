from flask import Blueprint, make_response, render_template, request, jsonify, redirect
import json
import cryptography

from utils import get_tokens, create_session, decrypt, OAuthError, validate_id_token
from config import AUTHORIZATION_SERVER_BASE_URI, TOKEN_ENDPOINT, CLIENT_ID, CLIENT_SECRET, SECRET, APP_HOST, REDIRECT_URI_ENDPOINT_DEFAULT, REDIRECT_URI_ENDPOINT_PKCE_BACK, REDIRECT_URI_ENDPOINT_PKCE_FRONT, REDIRECT_URI_ENDPOINT_FORM_POST


callbacks_bp = Blueprint('callbacks_bp', __name__)

# Route: Callback


@callbacks_bp.route('/callback', methods=['GET'])
def callback():
    try:
        code = request.args.get('code')
        if not code:
            raise ValueError('missing code parameter')
        token_request_url = f'{AUTHORIZATION_SERVER_BASE_URI}{TOKEN_ENDPOINT}'
        redirect_uri = f'{APP_HOST}{REDIRECT_URI_ENDPOINT_DEFAULT}'
        tokens = get_tokens(token_request_url, code, CLIENT_ID, CLIENT_SECRET, redirect_uri)
    except (OAuthError, ValueError) as e:
        error_data = {
            "type": e.__class__.__name__,
            "message": str(e),
        }
        return make_response(jsonify(error_data), 400)

    session_id = create_session(tokens.get('access_token'), tokens.get('id_token'))

    response = make_response(redirect("/main"))  # Redirect URL
    response.set_cookie('session_id', session_id,
                        httponly=True, samesite='Lax', secure=True)
    return response

# Route: Callback with PKCE


@callbacks_bp.route('/callback-pkce-front', methods=['GET'])
def callback_pkce_front():
    return render_template('callback-pkce-front.html')

# Route: Callback POST endpoint for PKCE


@callbacks_bp.route('/callback-pkce-post', methods=['POST'])
def callback_pkce_post():
    try:
        data = request.get_json()
        code = data.get('code')
        code_verifier = data.get('code_verifier')
        token_request_url = f'{AUTHORIZATION_SERVER_BASE_URI}{TOKEN_ENDPOINT}'
        redirect_uri = f'{APP_HOST}{REDIRECT_URI_ENDPOINT_PKCE_FRONT}'
        tokens = get_tokens(token_request_url, code, CLIENT_ID,
                            CLIENT_SECRET, redirect_uri, code_verifier)
    except OAuthError as e:
        error_data = {
            "type": e.__class__.__name__,
            "message": str(e),
        }
        return make_response(jsonify(error_data), 400)

    session_id = create_session(tokens.get('access_token'), tokens.get('id_token'))

    response = make_response(jsonify({'status': 'ok'}), 200)  # Redirect URL
    response.set_cookie('session_id', session_id,
                        httponly=True, samesite='Lax', secure=True) 
    return response


# Route: Callback PKCE back


@callbacks_bp.route('/callback-pkce-back', methods=['GET'])
def callback_pkce_back():
    try:
        pre_auth_session_decrypted = request.cookies.get('pre_auth_session')
        if not pre_auth_session_decrypted:
            raise ValueError('Missing pre_auth_session cookie')

        pre_auth_session = decrypt(pre_auth_session_decrypted, SECRET)
        pre_auth_session = json.loads(pre_auth_session)

        state = request.args.get('state')
        if state != pre_auth_session.get('state'):
            raise ValueError('State mismatch')

        code = request.args.get('code')
        code_verifier = pre_auth_session.get('code_verifier')
        token_request_url = f'{AUTHORIZATION_SERVER_BASE_URI}{TOKEN_ENDPOINT}'
        redirect_uri = f'{APP_HOST}{REDIRECT_URI_ENDPOINT_PKCE_BACK}'
        tokens = get_tokens(token_request_url, code, CLIENT_ID,
                            CLIENT_SECRET, redirect_uri, code_verifier)

    except (OAuthError, ValueError, json.JSONDecodeError, cryptography.fernet.InvalidToken) as e:
        error_data = {
            "type": e.__class__.__name__,
            "message": str(e),
        }
        return make_response(jsonify(error_data), 400)

    session_id = create_session(tokens.get('access_token'), tokens.get('id_token'))

    response = make_response(redirect("/pkce-back"))  # Redirect URL
    response.set_cookie('session_id', session_id,
                        httponly=True, samesite='Lax', secure=True)
    return response


# Route: Callback form post


@callbacks_bp.route('/callback-form-post', methods=['POST'])
def callback_form_post():
    try:
        pre_auth_session_decrypted = request.cookies.get('pre_auth_session')
        if not pre_auth_session_decrypted:
            raise ValueError('Missing pre_auth_session cookie')

        pre_auth_session = decrypt(pre_auth_session_decrypted, SECRET)
        pre_auth_session = json.loads(pre_auth_session)

        state = request.form.get('state')
        if state != pre_auth_session.get('state'):
            raise ValueError('State mismatch')

        nonce = pre_auth_session.get('nonce')

        code = request.form.get('code')
        code_verifier = pre_auth_session.get('code_verifier')
        token_request_url = f'{AUTHORIZATION_SERVER_BASE_URI}{TOKEN_ENDPOINT}'
        redirect_uri = f'{APP_HOST}{REDIRECT_URI_ENDPOINT_FORM_POST}'
        tokens = get_tokens(token_request_url, code, CLIENT_ID,
                            CLIENT_SECRET, redirect_uri, code_verifier)

        validate_id_token(tokens.get('id_token'), nonce)

    except (OAuthError, ValueError, json.JSONDecodeError, cryptography.fernet.InvalidToken) as e:
        error_data = {
            "type": e.__class__.__name__,
            "message": str(e),
        }
        return make_response(jsonify(error_data), 400)

    session_id = create_session(tokens.get('access_token'), tokens.get('id_token'))

    response = make_response(redirect("/form-post"))  # Redirect URL
    response.set_cookie('session_id', session_id,
                        httponly=True, samesite='Lax', secure=True)
    return response
