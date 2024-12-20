"""SQLAlchemy models"""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Follows(db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class Likes(db.Model):
    """Mapping user likes."""

    __tablename__ = 'likes' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='cascade')
    )

class Comments(db.Model):
    """Mapping user comments."""

    __tablename__ = 'comments' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='cascade')
    )

    def serialize(self):

        return {
            'id': self.id,
            'text': self.text,
            'timestamp': self.timestamp,
            'message_id': self.message_id,
            'user_id': self.user_id
        }    
        
    def __repr__(self):
        return f"{self.id}"


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    bio = db.Column(
        db.Text
    )

    location = db.Column(
        db.Text
    )

    password = db.Column(
        db.Text,
        nullable=False
    )


    likes = db.relationship(
        'Message',
        secondary="likes"
    )

    def serialize(self):

        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'image_url': self.image_url,
            'header_image_url': self.header_image_url,
            'bio': self.bio,
            'location': self.location,
            'password': self.password,
            'followers': list(map(str, self.followers)),
            'following': list(map(str, self.following)),
            'likes': list(map(str, self.likes))
        } 

    def __repr__(self):
        return f"{self.id}"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        """Find user with `username` and `password`.

        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return None

class Message(db.Model):
    """An individual Message/Post."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    text = db.Column(
        db.String(140),
        nullable=False
    )

    imageUrl = db.Column(
        db.Text
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    likes = db.relationship(
        'User',
        secondary="likes"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')

    def serialize(self):

        return {
            'id': self.id,
            'text': self.text,
            'imageUrl': self.imageUrl,
            'timestamp': self.timestamp,
            'likes': list(map(str, self.likes)),
            'user_id': self.user_id
        }    
        
    def __repr__(self):
        return f"{self.id}"


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

