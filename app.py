import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_from_directory, session, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from collections import Counter
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from flask_apispec import FlaskApiSpec, use_kwargs, marshal_with
from marshmallow import fields
from webargs.flaskparser import use_args
from schemas import SearchResponseSchema, SuggestResponseSchema, SearchHistoryResponseSchema
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from time import time
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegistrationForm
import secrets
from functools import wraps
from flask_wtf.csrf import CSRFProtect
import json


from extensions import db
from models import User, ClinicalStudy, Indication, Procedure, SearchLog

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Security configurations - must be set BEFORE initializing extensions
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.secret_key = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)  # Initialize secret key here

# Initialize CSRF protection AFTER secret key is set
csrf = CSRFProtect(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions AFTER secret key and CSRF are set
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#Example route demonstrating CSRF token generation and usage.  Replace with your actual routes.
@app.route('/test', methods=['GET', 'POST'])
def test_route():
    if request.method == 'GET':
        return render_template('test.html', csrf_token=session.get('csrf_token'))
    else:
        try:
            #Process POST request here
            return "Success!"
        except Exception as e:
            logger.exception(f"Error processing request: {e}")
            return f"Error: {e}", 500

# ... (rest of your routes and configurations) ...

# CSRF protection for all POST requests
@app.before_request
def csrf_protect():
    if request.method == "POST":
        # Skip CSRF for API endpoints
        if request.endpoint and request.endpoint.startswith('api_'):
            return

        token = request.headers.get('X-CSRF-Token')
        if not token and request.form:
            token = request.form.get('csrf_token')
        if not token or token != session.get('csrf_token'):
            abort(400, description="CSRF token validation failed")

@app.after_request
def after_request(response):
    # Ensure CSRF token exists in session
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return response

# Exempt API endpoints from CSRF
for endpoint in ['search', 'suggest', 'get_search_history', 'generate_api_token', 'save_search']:
    csrf.exempt(app.view_functions.get(endpoint))

if __name__ == '__main__':
    app.run(debug=True) # remember to change this to False for production