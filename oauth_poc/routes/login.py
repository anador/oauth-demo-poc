from flask import Blueprint, request, make_response, jsonify
import requests
# import json
# import logging
# from colorama import Style, Fore

from utils import generate_random_string, generate_code_challenge, create_pre_auth_session, session_data
from config import CLIENT_ID, REDIRECT_URI_ENDPOINT_DEFAULT, AUTHORIZATION_SERVER_BASE_URI, AUTHORIZATION_ENDPOINT, APP_HOST, REDIRECT_URI_ENDPOINT_PKCE_BACK, REDIRECT_URI_ENDPOINT_PKCE_FRONT, REDIRECT_URI_ENDPOINT_FORM_POST


login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/login/start', methods=['GET'])
def login():
    mode = request.args.get('mode', 'default')

    if mode == 'default':
        redirect_uri = f"{APP_HOST}{REDIRECT_URI_ENDPOINT_DEFAULT}"
    elif mode == 'pkce-front':
        redirect_uri = f"{APP_HOST}{REDIRECT_URI_ENDPOINT_PKCE_FRONT}"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "openid profile",
    }

    base_url = f'{AUTHORIZATION_SERVER_BASE_URI}{AUTHORIZATION_ENDPOINT}'
    authorization_request_url = requests.Request('GET', base_url, params=params).prepare().url
    response = {
        "url": authorization_request_url,
        "mode": mode
    }
    response = make_response(jsonify(response), 200)
    return response


@login_bp.route('/pkce/login/start', methods=['GET'])
def pkce_login():
    mode = request.args.get('mode', 'pkce-back')
    if mode == 'pkce-back':
        redirect_uri = f"{APP_HOST}{REDIRECT_URI_ENDPOINT_PKCE_BACK}"
    elif mode == 'form-post':
        redirect_uri = f"{APP_HOST}{REDIRECT_URI_ENDPOINT_FORM_POST}"

    code_verifier = generate_random_string()
    code_challenge = generate_code_challenge(code_verifier)
    state = generate_random_string(32)
    nonce = generate_random_string(22)

    pre_auth_session_data_encrypted = create_pre_auth_session(code_verifier, state, nonce)

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "openid profile",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
        "nonce": nonce
    }

    # When using form post response mode
    if mode == 'form-post':
        params['response_mode'] = 'form_post'
        samesite_flag = 'None'  # need to be set to let cookie be sent with POST request from form
    elif mode == 'pkce-back':
        samesite_flag = 'Lax'

    base_url = f'{AUTHORIZATION_SERVER_BASE_URI}{AUTHORIZATION_ENDPOINT}'
    authorization_request_url = requests.Request('GET', base_url, params=params).prepare().url
    response = {
        "url": authorization_request_url,
        "mode": mode
    }
    response = make_response(jsonify(response), 200)
    response.set_cookie('pre_auth_session', pre_auth_session_data_encrypted,
                        httponly=True, samesite=samesite_flag, max_age=180, secure=True) 
    return response


# Logout Route
@login_bp.route('/logout', methods=['POST'])
def logout():
    session_id = request.cookies.get('session_id')
    if session_id in session_data:
        del session_data[session_id]
    response = make_response("Logged out", 200)
    response.set_cookie('session_id', '', expires=0)
    return response
