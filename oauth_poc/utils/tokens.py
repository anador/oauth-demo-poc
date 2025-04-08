import requests
import logging
from colorama import Fore, Back, Style
import json

# from config import APP_HOST, REDIRECT_URI_ENDPOINT_DEFAULT
from utils.errors import OAuthError
from utils import decode_base64


def validate_id_token(id_token, nonce):

    # Do some necessary checks

    payload_decoded = decode_base64(id_token.split('.')[1])
    if json.loads(payload_decoded).get('nonce') != nonce:
        raise ValueError('Nonce mismatch')

    return True


def get_tokens(url, code, client_id, client_secret, redirect_uri, code_verifier=None):

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }
    # When using PKCE
    if code_verifier is not None:
        data['code_verifier'] = code_verifier

    response = requests.post(url, data=data, headers={
                             "Content-Type": "application/x-www-form-urlencoded"}, verify=False)
    if response.status_code >= 400:
        error_data = response.json()
        raise OAuthError(f"OAuth Error: {error_data.get(
            'error', 'unknown_error')} - {error_data.get('error_description', 'No description')}")

    tokens = response.json()
    logging.info(
        f"[Obtained tokens]\n\t{Back.GREEN}access_token: {tokens['access_token'][:100]}...{Style.RESET_ALL}\n\t{Fore.BLUE}id_token: {tokens['id_token'][:100]}...{Style.RESET_ALL}")

    return tokens  # Return successful token response
