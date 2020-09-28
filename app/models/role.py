from datetime import datetime
from typing import List

from . import db

class RoleModel(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    user_roles = db.relationship('UserRoleModel', lazy='dynamic')

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['RoleModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'RoleModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_role(cls, role:str) -> 'RoleModel':
        return cls.query.filter_by(role).first()

    @classmethod  
    def update(cls, id:int, role:str=None) -> None:
        record = cls.fetch_by_id(id)
        if role:
            record.role = role
        db.session.commit()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
