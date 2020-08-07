from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask import abort

from models.user_logs_model import UserLog, UserLogSchema

api = Namespace('logs', description='User Log Operations')

user_logs_schema = UserLogSchema()
user_logs_schema = UserLogSchema(many=True)

user_log_model = api.model('UserLog',{ 
    'method': fields.String(required=True, description='Method'),
    'description': fields.String(required=True, description='Description')
})

# get all logs - Admin
# get all logs by user - User, Admin, Customer care
# get all logs by session - User, Admin, Customer care
# post log - session
# get specific log - User, Admin, Customer care

@api.route('')
class ListAllLogs(Resource):
    @jwt_required
    @api.doc('list_all_user_logs')
    def get(self):
        '''List All Logs'''
        pass

    @jwt_required
    @api.doc('post_user_log')
    @api.expect(user_log_model)
    def post(self):
        '''Post User Log'''
        pass

@api.route('/<int:id>')
@api.param('id', 'The user log identifier')
class GetLog(Resource):
    @jwt_required
    @api.doc('get_specific_log')
    def get(self):
        '''Get specific Log'''
        pass


@api.route('/user/<int:id>')
@api.param('id', 'The user identifier')
class ListLogsByUser(Resource):
    @jwt_required
    @api.doc('list_logs_by_user')
    def get(self):
        '''List Logs by User'''
        pass

@api.route('/session/<int:id>')
@api.param('id', 'The session identifier')
class ListLogsByUser(Resource):
    @jwt_required
    @api.doc('list_logs_by_session')
    def get(self):
        '''List Logs by Session'''
        pass



