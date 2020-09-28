from datetime import datetime

from . import ma
from models.user import UserModel
from models.session import SessionModel
from schemas.user_logs import UserLogSchema

class SessionSchema(ma.SQLAlchemyAutoSchema):
    user_logs = ma.Nested(UserLogSchema, many=True)
    class Meta:
        model = SessionModel
        load_only = ('user',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'session_by_user': ma.URLFor('UserSessionList', id='<user_id>'),
        'collection': ma.URLFor('SessionList')
    })
        
