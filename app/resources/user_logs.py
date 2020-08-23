from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from models.user_logs_model import UserLog, UserLogSchema
from models.session_model import Session, SessionSchema

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
class ListAllLogs(Resource):
    @jwt_required
    @api.doc('List all user logs')
    def get(self):
        '''List All Logs'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if claims['is_admin']:
                my_logs = UserLog.fetch_all()
                logs = user_logs_schema.dump(my_logs)
                if len(logs) == 0:
                    return {'message': 'No user logs created yet.'}, 404
                return {'logs': logs}, 200
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

            # user_id = data['user_id']

            # fetch last/current session
            current_session = Session.fetch_current_user_session(user_id)
            session_id = current_session.id
            
            method = data['method'].lower()
            description = data['description'].lower()
            
            new_log = UserLog(session_id=session_id, method=method, description=description)
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
class GetLog(Resource):
    @jwt_required
    @api.doc('Get specific log')
    def get(self, id):
        '''Get specific Log'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            user_id = authorised_user['id']

            db_user_log = UserLog.fetch_by_id(id)
            user_log = user_log_schema.dump(db_user_log)
            if len(user_log) == 0:
                return{'message':'This user log does not exist.'}, 404

            requested_session = Session.fetch_by_id(id=db_user_log.session_id)

            if authorised_user['privileges'] == 'Customer care' or user_id == requested_session.user_id  or claims['is_admin'] :
                return {'log': user_log}, 200
            return {'message':'You are not authorised to view this log.'}, 403
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
    def get(self, session_id):
        '''List Logs by Session'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            user_id = authorised_user['id']

            # fetch last/current session
            current_session = Session.fetch_current_user_session(user_id)
            session_user = current_session.user_id
            
            requested_session = Session.fetch_by_id(id=session_id)
            session = session_schema.dump(requested_session)
            if len(session) == 0:
                return {'message': 'The requested session does not exist!'}, 404

            if authorised_user['privileges'] == 'Customer care' or requested_session.user_id == session_user  or claims['is_admin'] :
                db_user_logs = UserLog.fetch_by_session_id(session_id)
                user_logs = user_logs_schema.dump(db_user_logs)
                if len(user_logs) == 0:
                    return{'message':'These user logs do not exist.'}, 404
                return {'logs': user_logs}, 200
            return {'message':'You are not authorised to view this log.'}, 403
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
    def get(self, user_id):
        '''List Logs by User'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            user = authorised_user['id']

            # fetch last/current active session
            current_session = Session.fetch_current_user_session(user_id)
            this_session = session_schema.dump(current_session)
            if len(this_session) == 0:
                    return {'message':'This user does not exist.'}, 404
            
            session_user = current_session.user_id

            if authorised_user['privileges'] == 'Customer care' or user == user_id  or claims['is_admin'] :
                db_sessions = Session.fetch_by_user_id(user_id)

                session_ids = set()
                logs = []
                for session in db_sessions:
                    session_ids.add(session.id)
                print('Session IDS: ', session_ids)
                for session_id in session_ids:
                    db_user_logs = UserLog.fetch_by_session_id(session_id)
                    user_logs = user_logs_schema.dump(db_user_logs)
                    if len(user_logs) != 0:
                        for log in user_logs:
                            logs.append(log)
                if len(logs) == 0:
                    return {'message':'There are no logs for this user yet.'}, 404
                return {'logs': logs}, 200
            return {'message':'You are not authorised to view this log.'}, 403
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get user logs.'}, 500


