
from . import  ma
from models.user import UserModel
from schemas.user_role import UserRoleSchema
from schemas.password_reset import PasswordResetSchema
from schemas.session import SessionSchema

class UserSchema(ma.SQLAlchemyAutoSchema):
    user_roles = ma.Nested(UserRoleSchema, many=True)
    password_resets = ma.Nested(PasswordResetSchema, many=True)
    sessions = ma.Nested(SessionSchema, many=True)
    class Meta:
        model = UserModel
        load_only =('password', )
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('UserDetail', id='<id>'),
        'update': ma.URLFor('UpdateUser', id='<id>'),
        'collection': ma.URLFor('UserList')
    })
        
        
        
