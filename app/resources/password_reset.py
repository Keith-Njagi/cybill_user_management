import base64
import smtplib
from datetime import timedelta, datetime

import uuid
import requests
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, fresh_jwt_required, get_jwt_claims, get_jwt_identity
from flask import request, render_template
from .mail import mail, Message


from models.password_reset import PasswordResetModel
from models.user import UserModel
from models.user_role import UserRoleModel
from models.session import SessionModel
from schemas.password_reset import PasswordResetSchema
from schemas.user import UserSchema
from user_functions.token_generator import TokenGenerator
from user_functions.user_role_manager import UserPrivilege
from user_functions.compute_session_data import generate_device_data
from user_functions.record_user_log import record_user_log

api = Namespace('password', description='Change User Password')

password_reset_schema = PasswordResetSchema()
password_resets_schema = PasswordResetSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

reset_token_model = api.model('PasswordReset', {
    'email': fields.String(required=True, description='Email registered under one of the accounts')
})

password_reset_model = api.model('ChangePassword', {
    'password': fields.String(required=True, description='New Password')
})

log_submission_url = 'http://127.0.0.1:3100/api/logs'

@api.route('/forgot')
class SendResetLink(Resource):
    @api.doc('Send email with password reset link')
    @api.expect(reset_token_model)
    def post(self):
        '''Send email with password reset link'''
        data = api.payload

        if not data:
            return {'message': 'No input data detected'}, 400

        email = data['email'].lower()
        db_user = UserModel.query.filter_by(email=email).first()
        user_to_check = user_schema.dump(db_user)
        if len( user_to_check) == 0:
            return {'message': 'Failed! Please use the email used to register your account'}, 404

        password_reset = TokenGenerator()
        reset_code =password_reset.token_code
        reset_token = password_reset.url_token
        user_id = db_user.id
        password_reset_record = PasswordResetModel(user_id=user_id, reset_code=reset_code)
        password_reset_record.insert_record()
        try:
            # Add a html to send along with the email containing a button that redirects to the password reset page
            html_template = render_template('password_reset.html', reset_token=reset_token)
            txt_template = render_template('password_reset.txt', reset_token=reset_token)

            subject = "Password Reset"
            msg = Message('Password Change', sender='keithnjagicodingtrials@gmail.com', recipients=[email])
            msg.body = txt_template
            msg.html = html_template
            mail.send(msg)
            return {'message':'Please check your mail', 'reset_token':reset_token}, 200 # the reset token should be removed in production
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not send mail'}, 500

@api.route('/token/validity/<string:reset_token>')
class CheckTokenValidity(Resource):
    @api.doc('Verify password reset token')
    def get(self, reset_token:str):
        '''Verify Password Reset Token'''
        received_reset_token = reset_token
        try:
            TokenGenerator.decode_token(received_reset_token)
            token = TokenGenerator.token

            # Check for an existing reset_token with is_expired status as False
            reset_code_record = PasswordResetModel.fetch_by_reset_code(reset_code=token)
            if not reset_code_record:
                return{'message':'Rejected! This reset token does not exist'}, 404

            set_to_expire = reset_code_record.created + timedelta(minutes=30)
            current_time = datetime.utcnow()
            if set_to_expire <= current_time:
                user_id = reset_code_record.user_id
                is_expired = True
                user_records = PasswordResetModel.fetch_by_user_id(user_id)
                record_ids = []
                for record in user_records:
                    record_ids.append(record.id)
                for record_id in record_ids:
                    PasswordResetModel.expire_token(id=record_id, is_expired=is_expired)
                return {'message':'Rejected! Password reset token is expired. Please request a new password reset.'}, 403

            if reset_code_record.is_expired == True:
                user_id = reset_code_record.user_id
                is_expired = True
                user_records = PasswordResetModel.fetch_by_user_id(user_id)
                record_ids = []
                for record in user_records:
                    record_ids.append(record.id)
                for record_id in record_ids:
                    PasswordResetModel.expire_token(id=record_id, is_expired=is_expired)
                return {'message': 'Rejected! Password reset token has already been used. Please request a new password reset.'}, 403
            return {'message': 'You may type in your new password.'}, 200
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Operation NOT successful. Please use a valid token!!!'}, 500


@api.route('/reset/<string:reset_token>')
class ResetPassword(Resource):
    @api.doc('Reset password')
    @api.expect(password_reset_model)
    def put(self, reset_token:str):
        '''Reset User Password'''
        # Get User-agent and ip address 
        try:
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

            received_reset_token = reset_token
            TokenGenerator.decode_token(received_reset_token)
            token = TokenGenerator.token

            # Check for an existing reset_token with is_expired status as False
            reset_code_record = PasswordResetModel.fetch_by_reset_code(reset_code=token)
            if not reset_code_record:
                return{'message': 'This reset token does not exist'}, 404
            
            if reset_code_record.is_expired == True:
                user_id = reset_code_record.user_id
                is_expired = True
                user_records = PasswordResetModel.fetch_by_user_id(user_id)
                record_ids = []
                for record in user_records:
                    record_ids.append(record.id)
                for record_id in record_ids:
                    PasswordResetModel.expire_token(id=record_id, is_expired=is_expired)
                return {'message': 'Password reset token has already been used. Please request a new password reset.'}, 403

            user_id = reset_code_record.user_id
            is_expired = True
            user_records = PasswordResetModel.fetch_by_user_id(user_id)
            record_ids = []
            for record in user_records:
                record_ids.append(record.id)
            for record_id in record_ids:
                PasswordResetModel.expire_token(id=record_id, is_expired=is_expired)

            data = api.payload

            if not data:
                return {'message': 'No input data detected'}, 400

            password = data['password']
            hashed_password = generate_password_hash(data['password'], method='sha256')
            UserModel.update_password(id=user_id, password=hashed_password)

            this_user = UserModel.fetch_by_id(id=user_id)
            user = user_schema.dump(this_user)

            user_id = this_user.id

            # fetch User role
            user_role = UserRoleModel.fetch_by_user_id(user_id)
            privileges = user_role.role.role
            # Create access token
            expiry_time = timedelta(minutes=30)
            my_identity = {'id':this_user.id, 'privileges':privileges}
            access_token = create_access_token(identity=my_identity, expires_delta=expiry_time, fresh=True)
            refresh_token = create_refresh_token(my_identity)
            # Save session info to db
            new_session_record = SessionModel(user_ip_address=ip, device_operating_system=device_os, user_id=user_id)    
            new_session_record.insert_record()

            # Record this event in user's logs
            log_method = 'put'
            log_description = 'Password reset'
            
            auth_token  = { "Authorization": "Bearer %s" % access_token }
            record_user_log(auth_token, log_method, log_description)
            
            return {'user': user, 'access_token': access_token, "refresh_token": refresh_token}, 200
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not reset password.'}, 500



@api.route('/reset/list')
class PasswordResetList(Resource):
    @classmethod
    @fresh_jwt_required
    @api.doc('Fetch all password reset records')
    def get(cls):
        claims = get_jwt_claims()
        try:
            if claims['is_admin']:
                password_resets = PasswordResetModel.fetch_all()
                return password_resets_schema.dump(password_resets), 200
            return {'message':'You are not authorised to access this resource'}, 403
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not fetch password resets'}, 500

@api.route('reset/list/user')
class UserPasswordResetList(Resource):
    @classmethod
    @fresh_jwt_required
    @api.doc('Fetch all password reset records')
    def get(cls):
        authorised_user = get_jwt_identity()
        try:
            user_id =authorised_user['id']
            password_resets = PasswordResetModel.fetch_by_user_id(user_id=user_id)
            return password_resets_schema.dump(password_resets), 200
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not fetch password resets'}, 500

