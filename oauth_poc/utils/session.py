import hashlib
import base64
import json
import logging
from colorama import Fore, Style

from config import SECRET
from utils import encrypt

session_data = {}
# pre_auth_session_data = {}


def generate_SHA256(string):
    hash_object = hashlib.sha256(string.encode())  # Encode string and hash
    return hash_object.hexdigest()  # Get hexadecimal digest


def decode_base64(string):
    string += '=' * (4 - len(string) % 4)
    return base64.b64decode(string).decode('utf-8')


def get_user(session_id):
    user_data = session_data.get(session_id)
    if not user_data:
        return None

    id_token = user_data.get('id_token')
    
    # in real apps always validate the token first
    payload_decoded = decode_base64(id_token.split('.')[1])
    name = json.loads(payload_decoded).get('name')
    email = json.loads(payload_decoded).get('email')
    return {
        'name': name,
        'email': email
    }


def create_session(access_token, id_token):
    session_id = generate_SHA256(access_token)
    session_data[session_id] = {
        'access_token': access_token,
        'id_token': id_token,
    }
    logging.info(
        f"{Fore.YELLOW}Session created with id: {session_id}{Style.RESET_ALL}")
    return session_id


def create_pre_auth_session(code_verifier, state, nonce):
    pre_auth_session_data = {
        'code_verifier': code_verifier,
        'state': state,
        'nonce': nonce,
    }
    pre_auth_session_data = json.dumps(pre_auth_session_data)
    pre_auth_session_data_encrypted = encrypt(pre_auth_session_data, SECRET)
    logging.info(
        f"{Fore.LIGHTYELLOW_EX}Pre-auth session: {pre_auth_session_data_encrypted}{Style.RESET_ALL}")
    return pre_auth_session_data_encrypted
