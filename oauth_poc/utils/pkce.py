import base64
import hashlib
import os

def generate_random_string(length=43):
    random_bytes = os.urandom(length)
    return base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')


def generate_code_challenge(code_verifier):
    sha256_hash = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')