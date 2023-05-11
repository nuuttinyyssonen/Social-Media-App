from flask import Flask, render_template, redirect, url_for, request, session, Response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import base64
import random
from string import ascii_uppercase
from forms import *
from decouple import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database.db'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'nuutti.project@gmail.com'
app.config['MAIL_PASSWORD'] = config('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'nuutti.project@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

db = SQLAlchemy(app)
from models import *

login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
socketio = SocketIO(app)
s = URLSafeTimedSerializer('ThisIsSecret')

from queries import *

@app.before_first_request
def create_tables():
    db.create_all()

@login.user_loader
def load_user(id):
  return User.query.get(int(id))

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

# Login route to querie specific user
@app.route('/', methods=['GET', 'POST'])
def login():
    form = Login()
    # Execute only if form has data to submit
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        global user
        user = UserQueries.get_by_email(email)
        session['email'] = request.form.get('email')
        exists_email = UserQueries.exists_by_email(email)

        # Edge cases if user does not pass correct email or password
        if exists_email != True:
            flash('Invalid Email')
            return redirect(url_for('login'))

        # Another one
        if user is None or not user.check_password(password):
            flash('Invalid Password or Email')
            return redirect(url_for('login'))
        
        global user_id
        user_id = user.id
        login_user(user)
        next_page = request.args.get('next')

        # Redirecting user to nextpage
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('mainpage')
        return redirect(next_page)
    
    return render_template('login.html', form=form)


# Signup route to create users and store them in db
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = Signup()

    # Execute code only if form has data
    if form.validate_on_submit():
        password = form.password.data
        username = form.username.data
        email = form.email.data

        exists_username = UserQueries.exists_by_username(username)
        exists_email = UserQueries.exists_by_email(email)

        # Checking if user already exists in db with username or email
        if exists_username:
            print('This username is already in use!')
            return redirect(url_for('signup'))
        
        if exists_email:
            print('This email is already in use!')
            return redirect('signup')

        newUser = User(username=username, email=email, first_name=form.first_name.data, last_name=form.last_name.data)
        newUser.set_password(password)

        following = Following(user=newUser, following_count=0, following="")
        followers = Followers(user=newUser, followers_count=0, followers="")

        # adding users to db
        db.session.add(newUser, following)
        db.session.commit()
        db.session.add(followers)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

# Logout route for user to logout their account off the session
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logoutBtn = request.form.get('logout', False)
    # Execute when logoutBtn is clicked
    if logoutBtn != False:
        logout_user()
    return redirect(url_for('login'))

# reset route for user to be able to reset password via email
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = Reset()

    # Execute code only if form has data
    if form.validate_on_submit():

        global emailValue
        emailValue = form.email.data
        session['temporaryEmail'] = form.email.data
        token = s.dumps(emailValue, salt='password-reset')
        msg = Message('Password Reset', sender='nuutti.project@gmail.com', recipients=[emailValue])
        link = url_for('password_reset', token=token, _external=True)
        msg.body = 'Your link is {}'.format(link)
        mail.send(msg)
        flash('Message was semt successfully')

    return render_template('reset.html', form=form)

# Route for password reset when link from email is clicked
@app.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    # Try block to see if the token we are using is still valid meaning has the time expired yet
    try:
        s.loads(token, salt='password-reset', max_age=3600)
    except SignatureExpired:
        return render_template('signatureExpired.html')
    
    form = PasswordReset()
    # Execute code only if form has data
    if form.validate_on_submit():
        user = UserQueries.get_by_email(session['temporaryEmail'])
        if user:
            # if current User is valid then generate new password to it and update the specific db record
            new_password = generate_password_hash(form.password.data)
            User.query.filter_by(email=session['email']).update(dict(password=new_password))
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('noUser.html')
    
    return render_template('password_reset.html', form=form, token=token)

# Route for mainpage which contains most of applications features and links
@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    # All the necessary inputs and buttons are below
    upload = request.form.get('submit', False)
    profile = request.form.get('profile', False)
    commentBtn = request.form.get('commentBtn', False)
    commentvalue = request.form.get('comment')
    likeBtn = request.form.get('like', False)
    imageId = request.form.get('imageId')
    explore = request.form.get('explore', False)

    global searchFieldValue
    searchFieldValue = request.form.get('search')
    searchBtn = request.form.get('searchBtn', False)

    following_list = []
    image_list = []
    comments_list = []
    post = ""

    logged_in_user = UserQueries.get_by_email(session['email'])
    logged_in_user_id = logged_in_user.id
    logged_in_user_username = logged_in_user.username

    # users_following = Following.query.filter_by(parent_id=logged_in_user_id).first()
    users_following = FollowingQueries.get_by_id(logged_in_user_id)
    following_list = users_following.following.split(" ")

    # Looping thourgh all the ids in users following list to be able to display other users posts in logged in user's mainpage
    for id in following_list:
        if len(id) > 0:
            images = Img.query.filter_by(parent_id=id).all()
            singleImage = Img.query.filter_by(parent_id=id).first()
            image_list.append(images)

            singleImage_id = singleImage.id
            comments = Comments.query.filter_by(img_id=singleImage_id).all()
            comments_list.append(comments)
            post = zip(image_list, comments_list)


    if commentBtn != False:
        addComment = Comments(img_id=imageId, comments=commentvalue, username=logged_in_user_username)
        db.session.add(addComment)
        db.session.commit()

    if explore != False:
        return redirect(url_for('explore'))

    if upload != False:
        pic = request.files['pic']

        if not pic:
            return 'No pic uploaded', 400
    
        description = request.form.get('description')
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype

        db.session.expunge_all()

        img = Img(img=pic.read(), mimetype=mimetype, name=filename, description=description, author=session['email'], user=user, likes=0)
        db.session.add(img)
        db.session.commit()
        img = Img.query.filter_by(author=session['email'])

    if profile != False:
        return redirect(url_for('privateProfile', id=user_id))
    
    if searchBtn != False:
        exists = db.session.query(db.session.query(User).filter_by(username=searchFieldValue).exists()).scalar()

        if logged_in_user.username == searchFieldValue:
            print('you are this user')
            return redirect(url_for('mainpage'))
        elif exists:
            existing_user = User.query.filter_by(username=searchFieldValue).first()
            users_id = existing_user.id
            return redirect(url_for('singleProfiles', id=users_id))
        else:
            flash('User not found!')
            return redirect(url_for('mainpage'))
        

    return render_template('mainpage.html', image_list=image_list, post=post)

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    all_images = Img.query.all()
    random_images_list = []
    random_images_list_ids = []
    random_images = []

    for image in all_images:
        random_images_list.append(image.id)
    
    for id in random_images_list:
        if id not in random_images_list_ids:
            random_images_list_ids.append(id)
    
    random.shuffle(random_images_list_ids)
    
    for id in random_images_list_ids:
        random_images.append(Img.query.filter_by(id=id).first())
    
    return render_template('explore.html', random_images=random_images)

@app.route('/comments/<int:id>', methods=['GET', 'POST'])
def comments(id):
    img = Img.query.get(id)
    img.likes += 1
    db.session.commit()
    return redirect(url_for('mainpage'))

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    user = User.query.filter_by(email=session['email']).first()
    user_id = user.id
    exists = db.session.query(db.session.query(Img).filter_by(id=id).exists()).scalar()
    if exists == False:
        flash('Invalid img id')
        return redirect(url_for('privateProfile', id=user_id))

    img = Img.query.filter_by(id=id).first()
    db.session.delete(img)
    db.session.commit()
    return redirect(url_for('privateProfile', id=user_id))

def b64encode(data):
    return base64.b64encode(data).decode("UTF-8")

app.jinja_env.filters['zip'] = zip

app.jinja_env.filters['b64encode'] = b64encode

@app.route('/privateProfile/<int:id>', methods=['GET', 'POST'])
def privateProfile(id):
    logged_in_user = User.query.filter_by(email=session['email']).first()
    logged_in_user_id = logged_in_user.id
    logged_in_user_username = logged_in_user.username
    logged_in_user_first_name = logged_in_user.first_name
    logged_in_user_last_name = logged_in_user.last_name

    deleteBtn = request.form.get('deleteBtn', False)
    if deleteBtn != False:
        return redirect(url_for('delete'))

    followers = Followers.query.filter_by(parent_id=logged_in_user_id).first()
    followers_count = followers.followers_count

    following = Following.query.filter_by(parent_id=logged_in_user_id).first()
    following_count = following.following_count

    images = Img.query.filter_by(parent_id=id).all()
    post_count = (len(images))
    return render_template('profile.html', images=images, post_count=post_count, followers_count=followers_count, following_count=following_count, username=logged_in_user_username, logged_in_user_first_name=logged_in_user_first_name, logged_in_user_last_name=logged_in_user_last_name)

@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def singleProfiles(id):
    profile = User.query.filter_by(id=id).first()
    images = Img.query.filter_by(parent_id=id).all()
    sessionUser = User.query.filter_by(email=session['email']).first()
    sessionUser_id = sessionUser.id

    follower = Followers.query.filter_by(parent_id=id).first()
    following = Following.query.filter_by(parent_id=sessionUser_id).first()

    follower_count = follower.followers_count
    following_count = following.following_count
    post_count = len(images)

    following_boolean = False

    followBtn = request.form.get('follow', False)
    messageBtn = request.form.get('message', False)

    print(follower.followers)

    if str(sessionUser_id) in follower.followers:
        following_boolean = True

    if followBtn != False:

        follower.followers_count += 1
        follower.followers += str(sessionUser_id) + " "
        db.session.commit()

        following.following_count += 1
        following.following += str(id) + " "
        db.session.commit()
    
    if messageBtn != False:
        code = generate_unique_code(5)
        logged_in_user = User.query.filter_by(email=session['email']).first()
        other_user = User.query.filter_by(id=id).first()
        other_user_username = other_user.username
        logged_in_user_username = logged_in_user.username
        logged_in_user_id = logged_in_user.id
        roomNumber = ChatRooms(room_code=code, parent_id=logged_in_user_id, parent_id2=id, user1=logged_in_user_username, user2=other_user_username)
        db.session.add(roomNumber)
        db.session.commit()
        session['room'] = code
        room = code
        rooms[room] = {'members': 0, 'messages': []}
        return redirect(url_for('chat'))

    return render_template('singleprofile.html', images=images, profile=profile, post_count=post_count, id=id, follower_count=follower_count, following_count=following_count, following_boolean=following_boolean)

@app.route('/post/<int:id>', methods=['GET', 'POST'])
def singlePost(id):
    image = Img.query.filter_by(parent_id=id).first()
    return render_template('singlePost.html', image=image)


@app.route('/chat/inbox', methods=['GET', 'POST'])
def chatInbox():
    user = User.query.filter_by(email=session['email']).first()
    user_id = user.id
    chats = ChatRooms.query.filter_by(parent_id=user_id).all()
    more_chats = ChatRooms.query.filter_by(parent_id2=user_id).all()
    return render_template('chatInbox.html', chats=chats, more_chats=more_chats)

@app.route('/chat/<id>', methods=['GET', 'POST'])
def chatRoom(id):
    user = User.query.filter_by(email=session['email']).first()
    user_id = user.id
    chats = ChatRooms.query.filter_by(parent_id=user_id).all()
    more_chats = ChatRooms.query.filter_by(parent_id2=user_id).all()
    one_chat = ChatRooms.query.filter_by(room_code=id).first()

    chat_history = one_chat.chat_history_child
    session['room'] = id
    room = session.get('room')
    email = session.get('email')

    if room is None:
        return redirect(url_for('mainpage'))
    
    return render_template('chat.html', chats=chats, more_chats=more_chats, chat_history=chat_history, email=email)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    email = session.get('email')
    room = session.get('room')

    if room is None or email is None:
        return redirect(url_for('mainpage'))
    
    return render_template('chat.html')

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
    rooms[room]["messages"].append(content)
    print(f"message: {data['data']}")

@socketio.on('connect')
def connect():
    room = session.get('room')
    join_room(room)

@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    leave_room(room)