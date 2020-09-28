from . import ma

from models.user import UserModel
from models.password_reset import PasswordResetModel

class PasswordResetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PasswordResetModel
        load_only = ('user',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'collection': ma.URLFor('api.password_password_reset_list'),
        'password_resets_by_current_user': ma.URLFor('api.password_user_password_reset_list')
    })
        