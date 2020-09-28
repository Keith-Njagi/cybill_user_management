from datetime import datetime

from . import db, ma
from models.session import SessionModel
from models.user_logs import UserLogModel


class UserLogSchema(ma.SQLAlchemyAutoSchema):
    user_logs = ma.Nested(UserLogSchema, many=True)
    class Meta:
        model = UserLogModel
        load_only = ('session',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('UserLogDetail', id='<id>'),
        'collection': ma.URLFor('UserLogList'),
        'logs_by_session': ma.URLFor('ListLogsBySession', id='session_id'),
        'logs_by_user': ma.URLFor('ListLogsByUser', id='user_id')
    })
        
