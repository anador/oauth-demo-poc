from flask import Blueprint, render_template, request
import json

from utils import session_data, get_user

main_bp = Blueprint('main_bp', __name__)

# Route: Main Page


def render_main_page(title, login_function):
    user_cookie = request.cookies.get('session_id')
    if user_cookie != None and user_cookie in session_data:
        return render_template('main.html', message='Authenticated user', user=json.dumps(get_user(user_cookie)), title=title, login_function=login_function)
    else:
        return render_template('main.html', message='Guest (unathenticated)', title=title, login_function=login_function)


@main_bp.route('/main', methods=['GET'])
def main_page():
    return render_main_page('Main Page', 'login')

# Route: Main Page with PKCE


@main_bp.route('/pkce', methods=['GET'])
def pkce_main_page():
    return render_main_page('PKCE front', 'loginWithPKCE')

# Route: Main Page with PKCE back


@main_bp.route('/pkce-back', methods=['GET'])
def pkce_back_main_page():
    return render_main_page('PKCE back', 'loginWithPKCEBack')

# Route: Main page with form post response mode and PKCE back


@main_bp.route('/form-post', methods=['GET'])
def form_post_main_page():
    return render_main_page('Form Post', 'loginWithPKCEBackFormPost')
