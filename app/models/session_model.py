from datetime import datetime

from marshmallow import Schema, fields

from . import db, ma
from .user_model import User

class Session(db.Model):
    __tablename__='sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_ip_address = db.Column(db.String, nullable=False)
    device_operating_system  =  db.Column(db.String(25), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref("sessions", single_parent=True, lazy=True))
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
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True

class SessionSchema(ma.Schema):
    class Meta:
        fields = ('id','user_ip_address', 'device_operating_system', 'user_id', 'created')