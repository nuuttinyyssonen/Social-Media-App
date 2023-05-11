from models import *

class UserQueries():

    @classmethod
    def get_by_email(cls, email):
        return User.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_id(cls, id):
        return User.query.filter_by(id=id).first()
    
    @classmethod
    def exists_by_email(cls, email):
        return db.session.query(db.session.query(User).filter_by(email=email).exists()).scalar()
    
    @classmethod
    def exists_by_username(cls, username):
        return db.session.query(db.session.query(User).filter_by(username=username).exists()).scalar()


class FollowingQueries():

    @classmethod
    def get_by_id(cls, id):
        return Following.query.filter_by(id=id).first()