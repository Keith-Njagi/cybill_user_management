from datetime import datetime
from typing import List

from . import db

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    email =  db.Column(db.String(80), nullable=False, unique=True)
    phone =  db.Column(db.String(12), nullable=False, unique=True) #254718365458
    password = db.Column(db.String, nullable=False)
    is_suspended = db.Column(db.Integer, default=0, nullable=False)  # 0 is False, 1 is True, 2 is restored/False
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    user_roles = db.relationship('UserRoleModel', lazy=dynamic)
    password_resets = db.relationship('PasswordResetModel', lazy=dynamic)
    sessions = db.relationship('SessionModel', lazy=dynamic)

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> None:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'UserModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_email(cls, email:str) -> 'UserModel':
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def fetch_by_phone(cls, phone:str) -> 'UserModel':
        return cls.query.filter_by(phone=phone).first()

    @classmethod  
    def update(cls, id:int, full_name:str=None, email:str=None, phone:str=None) -> None:
        record = cls.fetch_by_id(id)
        if full_name:
            record.full_name = full_name
        if email:
            record.email = email
        if phone:
            record.phone = phone
        db.session.commit()

    @classmethod
    def update_password(cls, id:int, password:str=None) -> None:
        record = cls.fetch_by_id(id)
        if password:
            record.password = password
        db.session.commit()

    @classmethod
    def suspend(cls, id:int, is_suspended:int=None) -> None:
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()

    @classmethod
    def restore(cls, id:int, is_suspended:int=None) -> None:
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
