from datetime import timedelta

from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required

from models.user import UserModel
from models.user_role import UserRoleModel
from models.session import SessionModel
from schemas.user import UserSchema
from user_functions.user_role_manager import UserPrivilege
from user_functions.compute_session_data import generate_device_data


api = Namespace('login', description='Log in')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

my_user_model = api.model('Login', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password')

})


@api.route('')
class Login(Resource):
    @api.doc('Log in user')
    @api.expect(my_user_model)
    def post(self):
        '''Log in user'''
        try:
            # Get User-agent and ip address
            my_ip = request.environ.get('HTTP_X_FORWARDED_FOR')
            if my_ip is None:
                ip = request.environ['REMOTE_ADDR']
            else:
                ip = request.environ['HTTP_X_FORWARDED_FOR']

            if ip is None or str(ip) == '127.0.0.1'or str(ip) == '172.17.0.1':
                return{'message': 'This request has been rejected. Please use a recognised device'}, 403

            # Compute operating system and location
            device_operating_system = generate_device_data()
            if 'error' in device_operating_system.keys():
                return {'message': device_operating_system['error']}, 403
            device_os = device_operating_system['device_os']


            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            email = data['email']
            this_user = UserModel.fetch_by_email(email)
            if this_user:
                if check_password_hash(this_user.password, data['password']):
                    current_user = user_schema.dump(this_user)
                    user_id = this_user.id
                    # fetch User role
                    user_role = UserRoleModel.fetch_by_user_id(user_id)
                    # UserPrivilege.get_privileges(user_id = user_id, role= user_role.role)
                    # privileges = UserPrivilege.privileges
                    privileges = user_role.role.role
                    
                    # Create access token
                    expiry_time = timedelta(minutes=30)
                    my_identity = {'id':this_user.id, 'privileges':privileges}
                    access_token = create_access_token(identity=my_identity, expires_delta=expiry_time, fresh=True)
                    refresh_token = create_refresh_token(my_identity)
                    # Save session info to db
                    new_session_record = SessionModel(user_ip_address=ip, device_operating_system=device_os, user_id=user_id)    
                    new_session_record.insert_record()
                    return {'user': current_user, 'access_token': access_token, "refresh_token": refresh_token}, 200
            if not this_user or not check_password_hash(this_user.password, data['password']):
                return {'message': 'Could not log in, please check your credentials'}, 400
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not log in user.'}, 500

@api.route('/refresh')
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    @api.doc('Refresh JWT token')
    def post(self):
        '''Refresh JWT Token'''
        try:
            current_user = get_jwt_identity()
            new_token = create_access_token(identity=current_user, fresh=False)
            return {"access_token": new_token}, 200
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not refresh user login.'}, 500
