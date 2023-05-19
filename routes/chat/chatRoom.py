from flask import Blueprint, session, render_template, redirect, url_for
from ...Models.queries import *


chatRoom_bp = Blueprint('chatRoom_bp', __name__)

# This route is to specific chat room
@chatRoom_bp.route('/chat/<id>', methods=['GET', 'POST'])
def chatRoom(id):
    
    user = UserQueries.get_by_email(session['email'])
    user_id = user.id
    chats = ChatRooms.query.filter_by(parent_id=user_id).all()
    more_chats = ChatRooms.query.filter_by(parent_id2=user_id).all()
    one_chat = ChatRooms.query.filter_by(room_code=id).first()

    chat_history = one_chat.chat_history_child
    session['room'] = id
    room = session.get('room')
    email = session.get('email')

    if room is None:
        return redirect(url_for('mainpage_bp.mainpage'))
    
    return render_template('./chat/chat.html', chats=chats, more_chats=more_chats, chat_history=chat_history, email=email)
