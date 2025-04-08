# Authorization server params
AUTHORIZATION_SERVER_BASE_URI = '' # 'https://as.local:8443/realms/master/protocol/openid-connect'
AUTHORIZATION_ENDPOINT = '' # '/auth'
TOKEN_ENDPOINT = '' # '/token'

# Client settings
CLIENT_ID = ''
CLIENT_SECRET = ''
APP_HOST = '' # 'https://app.local'

REDIRECT_URI_ENDPOINT_DEFAULT = '/callback'
REDIRECT_URI_ENDPOINT_PKCE_FRONT = '/callback-pkce-front'
REDIRECT_URI_ENDPOINT_PKCE_BACK = '/callback-pkce-back'
REDIRECT_URI_ENDPOINT_FORM_POST = '/callback-form-post'

SECRET = 'Deathtopia-Virtuoso-Suicide-Master' # Used for encryption

# TLS settings
# TLS is disabled by default
SSL_CERT = "certs/app.local.crt"
SSL_KEY = "certs/app.local.key" 

