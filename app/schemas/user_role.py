from datetime import datetime


from . import ma
from models.user import UserModel
from models.role import RoleModel

class UserRoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RoleModel
        load_only = ('user','role',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('UserRoleDetail', id='<user_id>')
    })
        