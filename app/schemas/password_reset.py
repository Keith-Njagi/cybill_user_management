from . import ma

from models.password_reset import PasswordResetModel
from models.user import UserModel

class PasswordResetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PasswordResetModel
        load_only = ('user',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True
