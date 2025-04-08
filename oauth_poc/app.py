from flask import Flask
from flask_cors import CORS
import urllib3
import logging

from routes.main import main_bp
from routes.login import login_bp
from routes.callbacks import callbacks_bp
from routes.api import api_bp
from routes.xss import xss_bp
from config import SSL_CERT, SSL_KEY


# logging config
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(levelname)s: %(message)s", datefmt="%H:%M:%S")

# hack to hide SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
# CORS(app)
# logging.getLogger('werkzeug').disabled = True

# register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(login_bp)
app.register_blueprint(callbacks_bp)
app.register_blueprint(api_bp)
app.register_blueprint(xss_bp)


# Serve without TLS
# In this case be sure to provide a Secure context by any other means: https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts#when_is_a_context_considered_secure

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5555
    )


# Serve with TLS

# if __name__ == '__main__':
#     app.run(debug=True, host="127.0.0.1", port=443, ssl_context=(
#         SSL_CERT, SSL_KEY)
#     )