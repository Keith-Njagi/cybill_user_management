from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_raw_jwt, get_jwt_identity

from blacklist import BLACKLIST

api = Namespace('logout', description='Log out')

@api.route('')
class Logout(Resource):
    @api.doc('logout_user')
    @jwt_required
    def post(self):
        '''Log out user'''
        try:
            # jti is "JWT ID", a unique identifier for a JWT.
            jti = get_raw_jwt()["jti"]
            user = get_jwt_identity()
            user_id = user['id']
            BLACKLIST.add(jti)
            return {"message": f"User <id={user_id}> successfully logged out."}, 200
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not log out user.'}, 500
