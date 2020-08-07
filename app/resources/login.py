from datetime import timedelta

from flask import request, abort
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required

from models.user_model import User, UserSchema
from models.user_role_model import UserRole, UserRoleSchema
from models.session_model import Session
from user_functions.user_role_manager import UserPrivilege
from user_functions.compute_session_data import generate_device_data


api = Namespace('login', description='Log in')

user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_role_schema = UserRoleSchema()

my_user_model = api.model('Login', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password')

})


@api.route('')
class Login(Resource):
    @api.doc('login_user')
    @api.expect(my_user_model)
    def post(self):
        '''Log in user'''
        # Get User-agent and ip address
        my_ip = request.environ.get('HTTP_X_FORWARDED_FOR')
        if my_ip is None:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = request.environ['HTTP_X_FORWARDED_FOR']

        # if ip is None or str(ip) == '127.0.0.1'or str(ip) == '172.17.0.1':
        #     abort(400, 'This request has been rejected. Please use a recognised device')

        # Compute operating system and location
        device_operating_system = generate_device_data()
        if 'error' in device_operating_system.keys():
            abort(400, device_operating_system['error'])
        device_os = device_operating_system['device_os']


        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        email = data['email']
        this_user = User.fetch_by_email(email)
        if this_user:
            if check_password_hash(this_user.password, data['password']):
                current_user = user_schema.dump(this_user)
                user_id = this_user.id
                # fetch User role
                user_role = UserRole.fetch_by_user_id(user_id)
                # UserPrivilege.get_privileges(user_id = user_id, role= user_role.role)
                # privileges = UserPrivilege.privileges
                privileges = user_role.role.role
                
                # Create access token
                expiry_time = timedelta(minutes=30)
                my_identity = {'id':this_user.id, 'privileges':privileges}
                access_token = create_access_token(identity=my_identity, expires_delta=expiry_time)
                refresh_token = create_refresh_token(my_identity)
                # Save session info to db
                new_session_record = Session(user_ip_address=ip, device_operating_system=device_os, user_id=user_id)    
                new_session_record.insert_record()
                return {'user': current_user, 'access_token': access_token, "refresh_token": refresh_token}, 200
        if not this_user or not check_password_hash(this_user.password, data['password']):
            return {'message': 'Could not log in, please check your credentials'}, 400

@api.route('/refresh')
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    @api.doc('reset_token')
    def post(self):
        '''Reset JWT Token'''
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
