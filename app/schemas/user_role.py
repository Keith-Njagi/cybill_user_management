from datetime import datetime


from . import ma
from models.user import UserModel
from models.role import RoleModel
from models.user_role import UserRoleModel

class UserRoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserRoleModel
        load_only = ('user','role',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'roles_by_user': ma.URLFor('api.roles_user_role_detail', user_id='<user_id>')
    })
        