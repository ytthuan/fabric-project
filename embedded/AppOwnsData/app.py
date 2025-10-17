# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from services.pbiembedservice import PbiEmbedService
from utils import Utils
from flask import Flask, render_template, send_from_directory, redirect, url_for, session, request
import json
import os
from urllib.parse import urlencode
from authlib.integrations.requests_client import OAuth2Session
from flask_session import Session

# Initialize the Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object('config.BaseConfig')

# Configure session
app.secret_key = app.config.get('SESSION_SECRET') or os.urandom(32)
app.config['SESSION_TYPE'] = app.config.get('SESSION_TYPE', 'filesystem')
Session(app)

def _is_authenticated():
    return bool(session.get('user_email'))

def _build_authorize_url():
    authority = app.config['OIDC_AUTHORITY']
    client_id = app.config['CLIENT_ID']
    redirect_uri = app.config['OIDC_REDIRECT_URI']
    scope = ' '.join(app.config['OIDC_SCOPES'])
    authorize_endpoint = f"{authority}/oauth2/v2.0/authorize"
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'response_mode': 'query',
        'scope': scope,
        'state': os.urandom(16).hex(),
        'nonce': os.urandom(16).hex(),
    }
    session['oauth_state'] = params['state']
    session['oauth_nonce'] = params['nonce']
    return f"{authorize_endpoint}?{urlencode(params)}"

def _token_endpoint():
    return f"{app.config['OIDC_AUTHORITY']}/oauth2/v2.0/token"

@app.route('/')
def index():
    '''Returns a static HTML page'''
    if not _is_authenticated():
        return redirect(url_for('login'))
    return render_template('index.html', user_email=session.get('user_email'), user_name=session.get('user_name'))

@app.route('/getembedinfo', methods=['GET'])
def get_embed_info():
    '''Returns report embed configuration'''
    if not _is_authenticated():
        return redirect(url_for('login'))
    config_result = Utils.check_config(app)
    if config_result is not None:
        return json.dumps({'errorMsg': config_result}), 500

    try:
        embed_info = PbiEmbedService().get_embed_params_for_single_report(app.config['WORKSPACE_ID'], app.config['REPORT_ID'])
        return embed_info
    except Exception as ex:
        return json.dumps({'errorMsg': str(ex)}), 500

@app.route('/login')
def login():
    return redirect(_build_authorize_url())

@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state or state != session.get('oauth_state'):
        return json.dumps({'errorMsg': 'Invalid OAuth state'}), 400

    client = OAuth2Session(
        client_id=app.config['CLIENT_ID'],
        client_secret=app.config['CLIENT_SECRET'],
    )
    token = client.fetch_token(
        url=_token_endpoint(),
        grant_type='authorization_code',
        code=code,
        redirect_uri=app.config['OIDC_REDIRECT_URI'],
        scope=' '.join(app.config['OIDC_SCOPES'])
    )

    # Decode id_token claims with Authlib (without verification here; MS validates at token endpoint)
    id_token = token.get('id_token')
    if not id_token:
        return json.dumps({'errorMsg': 'No id_token in token response'}), 400

    # Minimal parsing: use MSAL to parse id token claims if available; otherwise a simple split-based decode
    try:
        from msal import IdTokenError, id_token as msal_id_token
        claims = msal_id_token.decode_id_token(id_token)
    except Exception:
        # Fallback: do a best-effort base64 decode of payload
        import base64, json as _json
        payload = id_token.split('.')[1]
        # pad base64url to multiple of 4
        padding = '=' * (-len(payload) % 4)
        claims = _json.loads(base64.urlsafe_b64decode(payload + padding).decode('utf-8'))

    # Optional nonce check when present
    nonce = session.get('oauth_nonce')
    if nonce and claims.get('nonce') and claims.get('nonce') != nonce:
        return json.dumps({'errorMsg': 'Invalid nonce in id_token'}), 400

    user_email = claims.get('preferred_username') or claims.get('upn') or claims.get('email')
    if not user_email:
        return json.dumps({'errorMsg': 'Unable to determine user email from id_token'}), 400
    session['user_email'] = user_email
    # Derive a friendly display name from claims or email alias
    display_name = claims.get('name') or user_email.split('@')[0]
    session['user_name'] = display_name

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    post_logout_redirect = app.config.get('POST_LOGOUT_REDIRECT_URI') or url_for('index', _external=True)
    session.clear()
    authority = app.config['OIDC_AUTHORITY']
    logout_url = f"{authority}/oauth2/v2.0/logout?{urlencode({'post_logout_redirect_uri': post_logout_redirect})}"
    return redirect(logout_url)

@app.route('/favicon.ico', methods=['GET'])
def getfavicon():
    '''Returns path of the favicon to be rendered'''

    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()