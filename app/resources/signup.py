from datetime import timedelta

from werkzeug.security import generate_password_hash
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token

from models.user import UserModel
from models.role import RoleModel
from models.user_role import UserRoleModel
from models.session import SessionModel
from schemas.user import UserSchema

from user_functions.user_role_manager import UserPrivilege
from user_functions.compute_session_data import generate_device_data

api = Namespace('signup', description='Register User')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

user_model = api.model('UserSignup', {
    'full_name': fields.String(required=True, description='Full Name'),
    'email': fields.String(required=True, description='Email'),
    'phone': fields.String(required=True, description='Phone'),
    'password': fields.String(required=True, description='Password')
})

@api.route('')
class RegisterUser(Resource):
    @api.expect(user_model)
    @api.doc('Register user')
    def post(self):
        '''Register User'''
        try:
            # Get User-agent and ip address 
            my_ip = request.environ.get('HTTP_X_FORWARDED_FOR')
            if my_ip is None:
                ip = request.environ['REMOTE_ADDR']
            else:
                ip = request.environ['HTTP_X_FORWARDED_FOR']

            if ip is None or str(ip) == '127.0.0.1' or str(ip) == '172.17.0.1':
                return {'message': 'This request has been rejected. Please use a recognised device'}, 403

            # Compute operating system
            device_operating_system = generate_device_data()
            if 'error' in device_operating_system.keys():
                return {'message': device_operating_system['error']}, 403
            device_os = device_operating_system['device_os']
        

            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            email = data['email'].lower()
            user = UserModel.fetch_by_email(email)
            if user:
                return {'message': 'Falied... A user with this email already exists'}, 400

            phone = data['phone']
            user = UserModel.fetch_by_phone(phone)
            if user:
                return {'message': 'Falied... A user with this phone number already exists'}, 400

            full_name = data['full_name'].lower()
            hashed_password = generate_password_hash(data['password'], method='sha256')
            # Save user to db
            new_user = UserModel(full_name=full_name, phone=phone, email=email, password=hashed_password)
            new_user.insert_record()

            # user = user_schema.dump(data) # This line would be used if we were outputing the user

            this_user = UserModel.fetch_by_email(email)

            UserPrivilege.generate_user_role(user_id = this_user.id)
            user_id = UserPrivilege.user_id
            role = UserPrivilege.role
            # Ensure all roles are saved to the db before registering the role to user
            db_roles = UserRoleModel.fetch_all()
            all_privileges = UserPrivilege.all_privileges
            if len(db_roles) == 0:
                for key, value in all_privileges.items():
                    new_role = RoleModel(role=value)
                    new_role.insert_record()
            # Link role to user
            new_user_role = UserRoleModel(user_id=user_id, role_id=role)
            new_user_role.insert_record()
            # Create access token
            
            privileges = UserPrivilege.privileges
            # privileges = user_role.role.role
            expiry_time = timedelta(minutes=30) # hours=1
            my_identity = {'id':this_user.id, 'privileges':privileges}
            access_token = create_access_token(identity=my_identity, expires_delta=expiry_time, fresh=True)
            refresh_token = create_refresh_token(my_identity)    
            # Save session info to db
            new_session_record = SessionModel(user_ip_address=ip, device_operating_system=device_os, user_id=user_id)    
            new_session_record.insert_record()
            return {'access token': access_token, "refresh_token": refresh_token }, 201
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not register user.'}, 500


