from flask import Blueprint, render_template

xss_bp = Blueprint('xss_bp', __name__)


@xss_bp.route('/xss', methods=['GET'])
def xss():
    return render_template('xss.html')
