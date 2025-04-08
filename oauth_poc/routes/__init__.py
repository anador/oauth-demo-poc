from flask import Blueprint

# import each blueprint
from .login import login_bp
from .callbacks import callbacks_bp
from .api import api_bp
from .xss import xss_bp

