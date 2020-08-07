import base64
import smtplib
from datetime import timedelta, datetime

import uuid
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import request, abort, render_template
from .mail import mail, Message

from models.user_model import User, UserSchema
from models.password_reset_model import PasswordReset, PasswordResetSchema
from models.user_role_model import UserRole, UserRoleSchema
from models.session_model import Session
from user_functions.token_generator import TokenGenerator
from user_functions.user_role_manager import UserPrivilege
from user_functions.compute_session_data import generate_device_data



api = Namespace('password', description='Change User Password')

password_reset_schema = PasswordResetSchema()
password_resets_schema = PasswordResetSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_role_schema = UserRoleSchema()

reset_token_model = api.model('PasswordResetToken', {
    'email': fields.String(required=True, description='Email registered under one of the accounts')
})

password_reset_model = api.model('ChangePassword', {
    'password': fields.String(required=True, description='New Password')
})


@api.route('/forgot')
class SendResetLink(Resource):
    @api.doc('create_reset_link')
    @api.expect(reset_token_model)
    def post(self):
        '''Send email with password reset link'''
        data = api.payload

        if not data:
            abort(400, 'No input data detected')

        email = data['email'].lower()
        db_user = User.query.filter_by(email=email).first()
        user_to_check = user_schema.dump(db_user)
        if len( user_to_check) == 0:
            abort(400, 'Failed! Please use the email used to register your account')

        password_reset = TokenGenerator()
        reset_code =password_reset.token_code
        reset_token = password_reset.url_token
        user_id = db_user.id
        password_reset_record = PasswordReset(user_id=user_id, reset_code=reset_code)
        password_reset_record.insert_record()
        print(reset_token)
        try:
            # Add a html to send along with the email containing a button that redirects to the password reset page
            html_template = render_template('password_reset.html', reset_token=reset_token)
            txt_template = render_template('password_reset.txt', reset_token=reset_token)

            subject = "Password Reset"
            msg = Message('Password Change', sender='keithnjagicodingtrials@gmail.com', recipients=[email])
            msg.body = txt_template
            msg.html = html_template
            # msg.attach(template, content_type='text/html; charset=UTF-8')

            mail.send(msg)
            return {'message':'Success', 'reset_token':reset_token}, 200
        except Exception as e:
            print('========================================')
            print('mail error description: ', e)
            print('========================================')
            return {'message': 'Couldn\'t send mail'}, 400

@api.route('/token/validity/<string:reset_token>')
class CheckTokenValidity(Resource):
    @api.doc('check_reset_password_token_validity')
    def get(self, reset_token):
        '''Verify Password Reset Token'''
        received_reset_token = reset_token
        try:
            TokenGenerator.decode_token(received_reset_token)
            token = TokenGenerator.token

            # Check for an existing reset_token with is_expired status as False
            reset_code_record = PasswordReset.fetch_by_reset_code(reset_code=token)
            if not reset_code_record:
                abort(400, 'Rejected! This reset token does not exist')

            set_to_expire = reset_code_record.created + timedelta(minutes=30)
            current_time = datetime.utcnow()
            if set_to_expire <= current_time:
                user_id = reset_code_record.user_id
                is_expired = True
                user_records = PasswordReset.fetch_by_user_id(user_id)
                record_ids = []
                for record in user_records:
                    record_ids.append(record.id)
                for record_id in record_ids:
                    PasswordReset.expire_token(id=record_id, is_expired=is_expired)
                abort(400, 'Rejected! Password reset token is expired. Please request a new password reset.')

            if reset_code_record.is_expired == True:
                user_id = reset_code_record.user_id
                is_expired = True
                user_records = PasswordReset.fetch_by_user_id(user_id)
                record_ids = []
                for record in user_records:
                    record_ids.append(record.id)
                for record_id in record_ids:
                    PasswordReset.expire_token(id=record_id, is_expired=is_expired)
                abort(400, 'Rejected! Password reset token has already been used. Please request a new password reset.')
            return {'message': 'You may type in your new password.'}, 200
        except Exception as e:
            return {'message': 'Operation NOT successful. Please use a valid token!!!'}


@api.route('/reset/<string:reset_token>')
class ResetPassword(Resource):
    @api.doc('reset_password')
    @api.expect(password_reset_model)
    def put(self, reset_token):
        '''Reset User Password'''
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

        received_reset_token = reset_token
        TokenGenerator.decode_token(received_reset_token)
        token = TokenGenerator.token

        # Check for an existing reset_token with is_expired status as False
        reset_code_record = PasswordReset.fetch_by_reset_code(reset_code=token)
        if not reset_code_record:
            abort(400, 'This reset token does not exist')
        
        if reset_code_record.is_expired == True:
            user_id = reset_code_record.user_id
            is_expired = True
            user_records = PasswordReset.fetch_by_user_id(user_id)
            record_ids = []
            for record in record_ids:
                record_ids.append(record.id)
            for record_id in record_ids:
                PasswordReset.expire_token(id=record_id, is_expired=is_expired)
            abort(400, 'Password reset token has already been used. Please request a new password reset.')

        user_id = reset_code_record.user_id
        is_expired = True
        user_records = PasswordReset.fetch_by_user_id(user_id)
        record_ids = []
        for record in user_records:
            record_ids.append(record.id)
        for record_id in record_ids:
            PasswordReset.expire_token(id=record_id, is_expired=is_expired)

        data = api.payload

        if not data:
            abort(400, 'No input data detected')

        password = data['password']
        hashed_password = generate_password_hash(data['password'], method='sha256')
        User.update_password(id=user_id, password=hashed_password)

        this_user = User.fetch_by_id(id=user_id)
        user = user_schema.dump(this_user)

        user_id = this_user.id

        # fetch User role
        user_role = UserRole.fetch_by_user_id(user_id)
        privileges = user_role.role.role
        # Create access token
        expiry_time = timedelta(minutes=30)
        my_identity = {'id':this_user.id, 'privileges':privileges}
        access_token = create_access_token(identity=my_identity, expires_delta=expiry_time)
        refresh_token = create_refresh_token(my_identity)
        # Save session info to db
        new_session_record = Session(user_ip_address=ip, device_operating_system=device_os, user_id=user_id)    
        new_session_record.insert_record()
        return {'message': 'Password changed and user logged in', 'user': user, 'access_token': access_token, "refresh_token": refresh_token}, 200
