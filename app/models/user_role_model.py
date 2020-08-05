from datetime import datetime

from marshmallow import Schema, fields

from . import db, ma
from .user_model import User
from .role_model import Role

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref("user_roles", single_parent=True, lazy=True))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref("user_roles", single_parent=True, lazy=True))

    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

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
    def fetch_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod  
    def update(cls, id, role_id=None):
        record = cls.fetch_by_id(id)

        if role_id:
            record.role_id = role_id
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True

class UserRoleSchema(ma.Schema):
    class Meta:
        fields =('id','user_id', 'role_id', 'created', 'updated')