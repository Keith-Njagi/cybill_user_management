from datetime import datetime
from ttyping import List


from . import db

class PasswordResetModel(db.Model):
    __tablename__ = 'password_resets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel')

    reset_code = db.Column(db.String(225), nullable=False)
    is_expired = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)


    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'PasswordResetModel':
        return cls.query.filter_by(id=id).first()

    @classmethod
    def fetch_by_reset_code(cls, reset_code:str)-> 'PasswordResetModel':
        return cls.query.filter_by(reset_code=reset_code).first()

    @classmethod
    def fetch_by_user_id(cls, user_id:int) -> List['PasswordResetModel']:
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def expire_token(cls, id:int, is_expired:bool=None) -> None:
        record = cls.fetch_by_id(id)
        if is_expired:
            record.is_expired = is_expired
        db.session.commit()
