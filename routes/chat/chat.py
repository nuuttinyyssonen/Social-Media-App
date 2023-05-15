from flask import Blueprint, session, render_template, redirect, url_for
from ...Models.queries import *

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/chat', methods=['GET', 'POST'])
def chat():
    email = session.get('email')
    room = session.get('room')

    if room is None or email is None:
        return redirect(url_for('mainpage_bp.mainpage'))
    
    return render_template('./chat/chat.html')