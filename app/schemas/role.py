
from . import  ma

from models.role import RoleModel
from schemas.user_role import UserRoleSchema

class RoleSchema(ma.SQLAlchemyAutoSchema):
    user_roles = ma.Nested(UserRoleSchema, many=True)
    class Meta:
        model = RoleModel
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'collection': ma.URLFor('RoleList')
    })
        
        