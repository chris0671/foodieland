import os
from cProfile import Profile
from crypt import methods

from flask import Flask, request, json, jsonify
# from flask_debugtoolbar import DebugToolbarExtension
from flask.helpers import send_from_directory
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User


CURR_USER_KEY = "curr_user"

app = Flask(__name__, static_folder='user/build', static_url_path='')

connect_db(app)

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# User register/login

@app.route("/register", methods=["POST"])
def register_user():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    user_exists = User.query.filter_by(email=email).first() is not None

    print(user_exists)

    if user_exists:
        return jsonify({"error": {"code": 401, "message": "User already exists"}}), 401

    user = User.signup(
                username=username,
                email=email,
                password=password
            )
    db.session.commit()

    return jsonify({
        "username": user.username,
        "email": user.email
    })

@app.route('/login', methods=["POST"])
def login():
    """Handle user login."""

    email = request.json["email"]
    password = request.json["password"]

    user = User.authenticate(                
                email=email,
                password=password
            )
    
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401        

    access_token = create_access_token(identity=email)

    return jsonify({
        "username": user.username,
        "email": user.email,
        "id": user.id,
        "access_token":access_token
    })

if __name__ == '__main__':
    app.run()        