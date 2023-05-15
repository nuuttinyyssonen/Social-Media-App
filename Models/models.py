from ..Extensions.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(180), index=True, unique=True)
    username = db.Column(db.String(180), index=True, unique=True)
    password = db.Column(db.String(180), index=True, unique=False)
    first_name = db.Column(db.String(180))
    last_name = db.Column(db.String(180))
    children_Img = db.relationship("Img", backref="user")
    children_Followers = db.relationship("Followers", backref="user")
    children_Following = db.relationship("Following", backref='user')
    children_ChatRooms = db.relationship('ChatRooms', backref='user')
   
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Followers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    followers_count = db.Column(db.Integer)
    followers = db.Column(db.String)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Following(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    following_count = db.Column(db.Integer)
    following = db.Column(db.String)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class Img(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    mimetype = db.Column(db.String, nullable=False)
    author = db.Column(db.String, index=True, unique=False)
    description = db.Column(db.String(500), unique=False, index=True)
    likes = db.Column(db.Integer())
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments_child = db.relationship("Comments", backref='img', lazy='subquery')

class Comments(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    comments = db.Column(db.String)
    username = db.Column(db.String)
    img_id = db.Column(db.Integer, db.ForeignKey('img.id'))

class ChatRooms(db.Model, UserMixin):

    __tablename__ = 'chatrooms'

    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id2 = db.Column(db.Integer)
    user1 = db.Column(db.String)
    user2 = db.Column(db.String)
    chat_history_child = db.relationship('ChatHistory', backref='chatrooms', lazy='subquery')

class ChatHistory(db.Model, UserMixin):

    __tablename__ = 'chathistory'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('chatrooms.id'))
    messages = db.Column(db.String)
    person = db.Column(db.String)