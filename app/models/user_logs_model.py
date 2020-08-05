from datetime import datetime

from marshmallow import Schema, fields

from . import db, ma
from .session_model import Session

class UserLog(db.Model):
    __tablename__='user_logs'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    session = db.relationship('Session', backref=db.backref("user_logs", single_parent=True, lazy=True))
    method  =  db.Column(db.String(25), nullable=False) # CRUD methods
    description = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    def insert_record(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetch_all(cls):
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def fetch_by_session_id(cls, session_id):
        return cls.query.filter_by(session_id=session_id).all()

    @classmethod
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True



class UserLogSchema(ma.Schema):
    class Meta:
        fields = ('id','session_id', 'method', 'description', 'created')