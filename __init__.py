from flask import Flask, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from .Models.models import *
from .Extensions.uniqueCode import rooms
from .Extensions.extensions import db, login, mail
from .routes.auth.login import login_bp
from .routes.auth.signup import signup_bp
from .routes.main.mainpage import mainpage_bp, comments_bp
from .routes.profiles.privateProfile import privateProfile_bp
from .routes.profiles.searchedProfile import searchedProfile_bp
from .routes.chat.chat import chat_bp
from .routes.chat.chatInbox import chatInbox_bp
from .routes.chat.chatRoom import chatRoom_bp
from .routes.main.explore import explore_bp, b64encode
from .routes.auth.reset import reset_bp, password_reset_bp
from .routes.auth.logout import logout_bp
from .routes.posts.singlePost import singlePost_bp
from decouple import config

app = Flask(__name__)
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')
app.config['MAIL_SERVER'] = config('MAIL_SERVER')
app.config['MAIL_USERNAME'] = config('MAIL_USERNAME')
app.config['MAIL_DEFAULT_SENDER'] = config('MAIL_DEFAULT_SENDER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_MAX_EMAIL'] = None
app.config['MAIL_ASCII_ATTACHMENT'] = False

db.init_app(app)
login.init_app(app)
mail.init_app(app)

if __name__ == '__main__':
    socketio.run(app)

@app.before_first_request
def create_tables():
    db.create_all()

app.jinja_env.filters['zip'] = zip
app.jinja_env.filters['b64encode'] = b64encode

@socketio.on('message')
def message(data):
    room = session.get('room')
    email = session.get('email')
    room_query = ChatRooms.query.filter_by(room_code=room).first()
    room_id = room_query.id
    content = {
        "message": data['data']
    }

    history = ChatHistory(messages=data['data'], parent_id=room_id, person=email)
    db.session.add(history)
    db.session.commit()
    send(content, to=room)
    print(f"message: {data['data']}")

@socketio.on('connect')
def connect():
    room = session.get('room')
    print('connected')
    join_room(room)

@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    print("left room")
    leave_room(room)

app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(mainpage_bp)
app.register_blueprint(privateProfile_bp)
app.register_blueprint(searchedProfile_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(chatInbox_bp)
app.register_blueprint(chatRoom_bp)
app.register_blueprint(explore_bp)
app.register_blueprint(reset_bp)
app.register_blueprint(password_reset_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(singlePost_bp)