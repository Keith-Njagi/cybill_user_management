from datetime import timedelta

from werkzeug.security import generate_password_hash
from flask import request, abort
from flask_restx import Namespace, Resource, fields
from flask_mail import Mail
from flask_jwt_extended import create_access_token, create_refresh_token

from models.user_model import User, UserSchema
from models.role_model import Role
from models.user_role_model import UserRole
from models.session_model import Session

from user_functions.user_role_manager import UserPrivilege
from user_functions.compute_session_data import generate_device_data

api = Namespace('signup', description='Register User')

mail = Mail()
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
    @api.doc('register_user')
    def post(self):
        '''Register User'''
        # Get User-agent and ip address 
        my_ip = request.environ.get('HTTP_X_FORWARDED_FOR')
        if my_ip is None:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = request.environ['HTTP_X_FORWARDED_FOR']

        # if ip is None or str(ip) == '127.0.0.1' or str(ip) == '172.17.0.1':
        #     abort(400, 'This request has been rejected. Please use a recognised device')

        # Compute operating system
        device_operating_system = generate_device_data()
        if 'error' in device_operating_system.keys():
            abort(400, device_operating_system['error'])
        device_os = device_operating_system['device_os']
       

        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        email = data['email'].lower()
        user = User.fetch_by_email(email)
        if user:
            abort(400, 'Falied... A user with this email already exists')

        phone = data['phone']
        user = User.fetch_by_phone(phone)
        if user:
            abort(400, 'Falied... A user with this phone number already exists')

        full_name = data['full_name'].lower()
        hashed_password = generate_password_hash(data['password'], method='sha256')
        # Save user to db
        new_user = User(full_name=full_name, phone=phone, email=email, password=hashed_password)
        new_user.insert_record()

        user = user_schema.dump(data)

        this_user = User.fetch_by_email(email)

        UserPrivilege.generate_user_role(user_id = this_user.id)
        user_id = UserPrivilege.user_id
        role = UserPrivilege.role
        # Ensure all roles are saved to the db before registering the role to user
        db_roles = UserRole.fetch_all()
        all_privileges = UserPrivilege.all_privileges
        if len(db_roles) == 0:
            for key, value in all_privileges.items():
                new_role = Role(role=value)
                new_role.insert_record()
        # Link role to user
        new_user_role = UserRole(user_id=user_id, role_id=role)
        new_user_role.insert_record()
        # Create access token
        
        privileges = UserPrivilege.privileges
        # privileges = user_role.role.role
        expiry_time = timedelta(minutes=30) # hours=1
        my_identity = {'id':this_user.id, 'privileges':privileges}
        access_token = create_access_token(identity=my_identity, expires_delta=expiry_time)
        refresh_token = create_refresh_token(my_identity)    
        # Save session info to db
        new_session_record = Session(user_ip_address=ip, device_operating_system=device_os, user_id=user_id)    
        new_session_record.insert_record()
        return {'access token': access_token, "refresh_token": refresh_token, 'user': user}, 201

