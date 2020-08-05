from datetime import datetime

from . import db, ma

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    email =  db.Column(db.String(80), nullable=False, unique=True)
    phone =  db.Column(db.Integer(12), nullable=False, unique=True) #254718365458
    password = db.Column(db.String, nullable=False)
    is_suspended = db.Column(db.Integer, default=0, nullable=False)  # 0 is False, 1 is True, 2 is restored/False
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
    def fetch_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def fetch_by_phone(cls, phone):
        return cls.query.filter_by(phone=phone).first()

    @classmethod  
    def update(cls, id, full_name=None, email=None, phone=None):
        record = cls.fetch_by_id(id)
        if full_name:
            record.full_name = full_name
        if email:
            record.email = email
        if phone:
            record.phone = phone
        db.session.commit()
        return True

    @classmethod
    def update_password(cls, id, password=None):
        record = cls.fetch_by_id(id)
        if password:
            record.password = password
        db.session.commit()
        return True

    @classmethod
    def suspend(cls, id, is_suspended=None):
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()
        return True

    @classmethod
    def restore(cls, id, is_suspended=None):
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'full_name', 'email', 'phone', 'is_suspended', 'created', 'updated')
