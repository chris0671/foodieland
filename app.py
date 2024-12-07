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

# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).limit(7).all()

    serialized = [u.serialize() for u in users]
    return jsonify(users=serialized)

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())


    serialized = user.serialize()
    serializedTwo = [m.serialize() for m in messages]

    return jsonify(user=serialized, messages=serializedTwo)

@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    user = User.query.get_or_404(user_id)
    serialized = user.serialize()
    return jsonify(user=serialized)

@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    user = User.query.get_or_404(user_id)
    serialized = user.serialize()
    return jsonify(user=serialized)

@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""
    userId = request.json["userId"]

    followed_user = User.query.get_or_404(follow_id)
    user = User.query.get_or_404(userId)
    user.following.append(followed_user)
    db.session.commit()

    return jsonify({"user": "following added"})    

@app.route('/users/unfollow/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""
    userId = request.json["userId"]
    user = User.query.get_or_404(userId)

    followed_user = User.query.get(follow_id)
    user.following.remove(followed_user)
    db.session.commit()

    return jsonify({"user": "unfollowed user"})  

@app.route('/users/<int:user_id>/update', methods=["POST"])
def profile(user_id):
    """Update profile for current user."""

    email = request.json["email"]
    username = request.json["username"]
    image_url = request.json["image_url"]
    header_image_url = request.json["header_image_url"]

    user = User.query.get_or_404(user_id)

    if(user):
            user.email = email
            user.username = username
            user.image_url = image_url
            user.header_image_url = header_image_url

            db.session.commit()

            return jsonify({"user": "edit user profile successful"})  
    
@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Delete user."""
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"user": "user account deleted"})  

if __name__ == '__main__':
    app.run()        