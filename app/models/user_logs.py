from datetime import datetime
from typing import List

from . import db

class UserLogModel(db.Model):
    __tablename__='user_logs'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    session = db.relationship('SessionModel')
    method  =  db.Column(db.String(25), nullable=False) # CRUD methods
    description = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['UserLogModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'UserLogModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_session_id(cls, session_id:int) -> List['UserLogModel']:
        return cls.query.filter_by(session_id=session_id).all()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
