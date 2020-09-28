from datetime import datetime
from typing import List

from . import db

class UserRoleModel(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel')

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('RoleModel')

    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['UserRoleModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'UserRoleModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_user_id(cls, user_id:int) -> 'UserRoleModel':
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod  
    def update(cls, id:int, role_id:int=None) -> None:
        record = cls.fetch_by_id(id)

        if role_id:
            record.role_id = role_id
        db.session.commit()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
