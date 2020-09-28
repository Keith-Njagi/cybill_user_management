from datetime import timedelta

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask import request

from models.user import UserModel
from schemas.user import UserSchema
from user_functions.record_user_log import record_user_log


api = Namespace('user', description='Manage User')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@api.route('')
class UserList(Resource):
    @api.doc('List all users')
    @jwt_required
    def get(self):
        '''List all Users'''
        try:
            claims = get_jwt_claims()
            print(claims)
            authorised_user = get_jwt_identity()
            if authorised_user['privileges'] == 'Customer care' or claims['is_admin'] :
                users = UserModel.fetch_all()
                
                # Record this event in user's logs
                log_method = 'get'
                log_description = 'Fetched all users'

                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return users_schema.dump(users), 200
            return {'message':'You do not have the required permissions!'}, 403
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get users.'}, 500

@api.route('/<int:id>')
@api.param('id', 'The user identifier')
class UserDetail(Resource):
    @api.doc('Get specific user')
    @jwt_required
    def get(self, id:int):
        '''Get Specific User'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if authorised_user['privileges'] == 'Customer care' or id == authorised_user['id']  or claims['is_admin'] :
                user = UserModel.fetch_by_id(id)
                if user:
                    # Record this event in user's logs
                    log_method = 'get'
                    log_description = 'Fetched user <' + str(id) + '>'

                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)
                    
                    return user_schema.dump(user), 200
                return {'message': 'User does not exist'}, 404             
            return {'message': 'You are not authorised to view this user!'}, 403
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get user.'}, 500


@api.route('/suspend/<int:id>')
@api.param('id', 'The user identifier')
class SuspendUser(Resource):
    @api.doc('Suspend user')
    @jwt_required
    def put(self, id:int):
        '''Suspend User'''
        user = UserModel.fetch_by_id(id) 
        if user:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if claims['is_admin'] or id == authorised_user['id']:
                is_suspended = 1
                try:
                    UserModel.suspend(id, is_suspended=is_suspended)

                    # Record this event in user's logs
                    log_method = 'put'
                    log_description = 'Suspended user <' + str(id) + '>'

                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)

                    return {'message': 'User suspended successfuly'}, 200
                except Exception as e:
                    print('========================================')
                    print('error description: ', e)
                    print('========================================')
                    return {'message': 'Could not suspend user.'}, 500

            return {'message': 'You do not have the required permissions to modify this user!'}, 403
        return {'message': 'User does not exist'}, 404

        
@api.route('/restore/<int:id>')
@api.param('id', 'The user identifier')
class RestoreUser(Resource):
    @api.doc('Restore user')
    @jwt_required
    def put(self, id:int):
        '''Restore User'''
        user = UserModel.fetch_by_id(id)
        if user:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if claims['is_admin'] or id == authorised_user['id']:
                is_suspended = 2
                try:
                    UserModel.restore(id=id, is_suspended=is_suspended)

                    # Record this event in user's logs
                    log_method = 'put'
                    log_description = 'Restored user <' + str(id) + '>'

                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)

                    return {'message': 'User restored successfuly'}, 200
                except Exception as e:
                    print('========================================')
                    print('error description: ', e)
                    print('========================================')
                    return{'message': 'Unable to restore user.'}, 500

            return {'message':'You do not have the required permissions to modify this user!'}, 403
        return {'message': 'User does not exist'}, 404

        
@api.route('/delete/<int:id>')
@api.param('id', 'The user identifier')
class DeleteUser(Resource):
    @api.doc('Delete user')
    @jwt_required
    def delete(self, id:int):
        '''Delete User'''
        try:
            my_user = UserModel.fetch_by_id(id)
            user = user_schema.dump(my_user)
            if user:
                claims = get_jwt_claims()
                authorised_user = get_jwt_identity()
                if not claims['is_admin'] or id != authorised_user['id']: # 403
                    return {'message':'You do not have the required permissions to delete this user!'}, 403

                UserModel.delete_by_id(id)

                # Record this event in user's logs
                log_method = 'delete'
                log_description = 'Deleted user <' + str(id) + '>'

                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return {'message': 'User deleted successfuly'}, 200
            return {'message': 'User does not exist'}, 404

        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not delete user.'}, 500
