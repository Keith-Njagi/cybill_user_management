from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from models.user_logs import UserLogModel
from models.session import SessionModel
from schemas.user_logs import UserLogSchema
from schemas.session import SessionSchema

api = Namespace('logs', description='User Log Operations')

user_log_schema = UserLogSchema()
user_logs_schema = UserLogSchema(many=True)
session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

user_log_model = api.model('UserLog',{ 
    'method': fields.String(required=True, description='Method'),
    'description': fields.String(required=True, description='Description')
})

# get all logs - Admin
# post log - session
@api.route('')
class UserLogList(Resource):
    @jwt_required
    @api.doc('List all user logs')
    def get(self):
        '''List All Logs'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if claims['is_admin']:
                logs = UserLogModel.fetch_all()
                if logs:
                    return user_logs_schema.dump(logs), 200
                return {'message': 'No user logs created yet.'}, 404
            return {'message': 'You are not authorised to view this information!'}, 403
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not fetch user logs.'}, 500

    @jwt_required
    @api.doc('Post user log')
    @api.expect(user_log_model)
    def post(self):
        '''Post User Log'''
        try:
            authorised_user = get_jwt_identity()
            user_id = authorised_user['id']

            data = api.payload
            if not data:
                return {'message':'No input data detected'}, 400

            # fetch last/current session
            current_session = SessionModel.fetch_current_user_session(user_id)
            session_id = current_session.id
            
            method = data['method'].lower()
            description = data['description'].lower()
            
            new_log = UserLogModel(session_id=session_id, method=method, description=description)
            new_log.insert_record()

            return{'message':'User log added successfully'}, 201
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not submit user log to database.'}, 500



# get specific log - User, Admin, Customer care
@api.route('/<int:id>')
@api.param('id', 'The user log identifier')
class UserLogdetail(Resource):
    @jwt_required
    @api.doc('Get specific log')
    def get(self, id:int):
        '''Get specific Log'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            user_id = authorised_user['id']

            user_log = UserLogModel.fetch_by_id(id)
            
            if user_log:
                requested_session = SessionModel.fetch_by_id(id=db_user_log.session_id)
                if authorised_user['privileges'] == 'Customer care' or user_id == requested_session.user_id  or claims['is_admin'] :
                    return user_log_schema.dump(user_log), 200
                return {'message':'You are not authorised to view this log.'}, 403
            return{'message':'This user log does not exist.'}, 404   
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not fetch user log.'}, 500


# get all logs by session - User, Admin, Customer care
@api.route('/session/<int:session_id>')
@api.param('session_id', 'The session identifier')
class ListLogsBySession(Resource):
    @jwt_required
    @api.doc('List logs by session')
    def get(self, session_id:int):
        '''List Logs by Session'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            user_id = authorised_user['id']

            # fetch last/current session
            current_session = SessionModel.fetch_current_user_session(user_id)
            session_user = current_session.user_id
            
            session = SessionModel.fetch_by_id(id=session_id)
            if session:
                if authorised_user['privileges'] == 'Customer care' or requested_session.user_id == session_user  or claims['is_admin'] :
                    user_logs = UserLogModel.fetch_by_session_id(session_id)
                    if user_logs:
                        return user_logs_schema.dump(user_logs), 200
                    return{'message':'These user logs do not exist.'}, 404                 
                return {'message':'You are not authorised to view this log.'}, 403
            return {'message': 'The requested session does not exist!'}, 404

            
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get user logs.'}, 500


# get all logs by user - User, Admin, Customer care
@api.route('/user/<int:user_id>')
@api.param('user_id', 'The user identifier')
class ListLogsByUser(Resource):
    @jwt_required
    @api.doc('List logs by user')
    def get(self, user_id:int):
        '''List Logs by User'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            user = authorised_user['id']

            # fetch last/current active session
            current_session = SessionModel.fetch_current_user_session(user_id)
            if current_session:
                session_user = current_session.user_id

                if authorised_user['privileges'] == 'Customer care' or user == user_id  or claims['is_admin'] :
                    db_sessions = Session.fetch_by_user_id(user_id)

                    session_ids = set()
                    logs = []
                    for session in db_sessions:
                        session_ids.add(session.id)
                    for session_id in session_ids:
                        db_user_logs = UserLog.fetch_by_session_id(session_id)
                        user_logs = user_logs_schema.dump(db_user_logs)
                        if len(user_logs) != 0:
                            for log in user_logs:
                                logs.append(log)
                    if len(logs) == 0:
                        return {'message':'There are no logs for this user yet.'}, 404
                    return logs, 200
                return {'message':'You are not authorised to view this log.'}, 403
            return {'message':'This user does not exist.'}, 404
            
            
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get user logs.'}, 500


