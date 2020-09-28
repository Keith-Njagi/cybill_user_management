from datetime import datetime

from . import  ma
from models.session import SessionModel
from models.user_logs import UserLogModel


class UserLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserLogModel
        load_only = ('session',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.logs_user_log_detail', id='<id>'),
        'collection': ma.URLFor('api.logs_user_log_list'),
        'logs_by_session': ma.URLFor('api.logs_list_logs_by_session', session_id='<session_id>'),
        'logs_by_user': ma.URLFor('api.logs_list_logs_by_user', user_id='<id>')
    })
        
