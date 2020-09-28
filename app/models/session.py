from datetime import datetime
from typing import List

from . import db

class SessionModel(db.Model):
    __tablename__='sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_ip_address = db.Column(db.String, nullable=False)
    device_operating_system  =  db.Column(db.String(25), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel')
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    user_logs = db.relationship('UserLogModel', lazy=dynamic)

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['SessionModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'SessionModel':
        return cls.query.get(id)

    
    @classmethod
    def fetch_by_user_id(cls, user_id:int) -> List['SessionModel']:
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def fetch_current_user_session(cls, user_id:int) -> 'SessionModel':
        return cls.query.filter_by(user_id=user_id).order_by(cls.id.desc()).first()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
