from datetime import timedelta

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask import abort, jsonify
from werkzeug.exceptions import BadRequest

from models.user_model import User, UserSchema

api = Namespace('user', description='Manage User')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@api.route('')
class UserList(Resource):
    @api.doc('list_users')
    @jwt_required
    def get(self):
        '''List all Users'''
        claims = get_jwt_claims()
        print(claims)
        authorised_user = get_jwt_identity()
        if authorised_user['privileges'] == 'Customer care' or claims['is_admin'] :
            my_users = User.fetch_all()
            users = users_schema.dump(my_users)
            return {'users': users}, 200
        abort(400, 'You do not have the required permissions!')

@api.route('/<int:id>')
@api.param('id', 'The user identifier')
class GetUser(Resource):
    @api.doc('get_user')
    @jwt_required
    def get(self, id):
        '''Get Specific User'''
        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        if authorised_user['privileges'] == 'Customer care' or user_id == authorised_user['id']  or claims['is_admin'] :
            my_user = User.fetch_by_id(id)
            user = user_schema.dump(my_user)

            if len(user) == 0:
                abort(400, 'User does not exist')
            
            return {'user': user}, 200
        return {'message': 'You are not authorised to view this user!'}


@api.route('/suspend/<int:id>')
@api.param('id', 'The user identifier')
class SuspendUser(Resource):
    @api.doc('suspend_user')
    @jwt_required
    def put(self, id):
        '''Suspend User'''
        my_user = User.fetch_by_id(id)
        user = user_schema.dump(my_user)
        if len(user) == 0:
            abort(400, 'User does not exist')

        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        if claims['is_admin'] or id == authorised_user['id']:
            is_suspended = 1
            try:
                User.suspend(id, is_suspended=is_suspended)
                return {'message': 'User suspended successfuly'}, 200
            except:
                return{'message': 'Unable to perform this action'}, 400

        abort(400, 'You do not have the required permissions to modify this user!')


@api.route('/restore/<int:id>')
@api.param('id', 'The user identifier')
class RestoreUser(Resource):
    @api.doc('restore_user')
    @jwt_required
    def put(self, id):
        '''Restore User'''
        my_user = User.fetch_by_id(id)
        user = user_schema.dump(my_user)
        if len(user) == 0:
            abort(400, 'User does not exist')

        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        if claims['is_admin'] or id == authorised_user['id']:
            is_suspended = 2
            try:
                User.restore(id=id, is_suspended=is_suspended)
                return {'message': 'User restored successfuly'}, 200
            except:
                return{'message': 'Unable to perform this action'}, 400

        abort(400, 'You do not have the required permissions to modify this user!')


@api.route('/delete/<int:id>')
@api.param('id', 'The user identifier')
class DeleteUser(Resource):
    @api.doc('delete_user')
    @jwt_required
    def delete(self, id):
        '''Delete User'''
        my_user = User.fetch_by_id(id)
        user = user_schema.dump(my_user)
        if len(user) == 0:
            abort(400, 'User does not exist')

        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        if not claims['is_admin'] or id != authorised_user['id']: # 403
            abort(400, 'You do not have the required permissions to delete this user!')

        User.delete_by_id(id)

        return {'message': 'User deleted successfuly'}, 200
