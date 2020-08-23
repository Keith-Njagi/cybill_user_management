from werkzeug.security import generate_password_hash
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from flask import request

from models.role_model import Role, RoleSchema
from models.user_role_model import UserRole, UserRoleSchema
from user_functions.user_role_manager import UserPrivilege
from user_functions.record_user_log import record_user_log


api = Namespace('roles', description='User Role Operations')

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)
user_role_schema = UserRoleSchema()
user_roles_schema = UserRoleSchema(many=True)

user_role_model = api.model('UserRole', {
    'role': fields.Integer(required=True, description='Role'),
})


@api.route('')
class RoleList(Resource):
    @api.doc('Get all user oles')
    @jwt_required
    def get(self):
        '''Get All User Roles'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if claims['is_admin']:
                db_roles = Role.fetch_all()
                roles = roles_schema.dump(db_roles)

                # Record this event in user's logs
                log_user_id = authorised_user['id']
                log_method = 'get'
                log_description = 'Fetched all roles'
                # record_user_log(log_user_id, log_method, log_description)
                
                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return {'roles':roles}
            return {'message':'You do not have the required permissions!'}, 400
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get user roles.'}, 500


@api.route('/user/<int:id>')
@api.param('id', 'The role identifier')
class UserRoleList(Resource):
    @api.doc('Get user role')
    @jwt_required
    def get(self, id):
        '''Get User Role'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if not claims['is_admin']:
                return {'message': 'You do not have the required permissions!'}, 403

            role_record = UserRole.fetch_by_user_id(id)
            if role_record:
                # user_role = user_role_schema.dump(role_record)
                user_role = role_record.role.role

                # Record this event in user's logs
                log_user_id = authorised_user['id']
                log_method = 'get'
                log_description = 'Fetched role for user <' + str(id) + '>'
                # record_user_log(log_user_id, log_method, log_description)
                
                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return {'role': user_role}, 200
            return {'message': 'Record not found'}, 404
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get user role.'}, 500


    @api.doc('Update a user role')
    @api.expect(user_role_model)
    @jwt_required
    def put(self, id):
        '''Update a User Role'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if not claims['is_admin']:
                return {'message':'You do not have the required permissions!'}, 403

            data = api.payload
            if not data:
                return {'message':'No input data detected'}, 400

            role_record = UserRole.fetch_by_user_id(id)
            if role_record:
                role = data['role']
                id = role_record.id
                UserRole.update(id, role_id=role)
                # user_role = user_role_schema.dump(role_record)
                user_role = role_record.role.role

                # Record this event in user's logs
                log_method = 'put'
                log_description = 'Updated role for user <' + str(id) + '>'

                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return {'role': user_role}, 200
            return {'message': 'Record not found'}, 404
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not update user role.'}, 500

