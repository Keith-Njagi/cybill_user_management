from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from models.session_model import Session, SessionSchema

api = Namespace('session', description='User Session Operations')

session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)


@api.route('')
class SessionList(Resource):
    @api.doc('List sessions')
    @jwt_required
    def get(self):
        '''List Sessions'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()
            if authorised_user['privileges'] == 'Customer care' or claims['is_admin'] :
                my_sessions = Session.fetch_all()
                sessions = sessions_schema.dump(my_sessions)
                return {'sessions': sessions}, 200
            user_id = authorised_user['id']
            my_sessions = Session.fetch_by_user_id(user_id)
            sessions = sessions_schema.dump(my_sessions)
            return { 'sessions': sessions}, 200
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get sessions.'}, 500



@api.route('/user/<int:user_id>')
@api.param('user_id', 'The user identifier')
class UserSessionList(Resource):
    @api.doc('List user sessions')
    @jwt_required
    def get(self, user_id):
        '''List User Sessions'''
        try:
            claims = get_jwt_claims()
            authorised_user = get_jwt_identity()

            if authorised_user['privileges'] == 'Customer care' or user_id == authorised_user['id']  or claims['is_admin'] :
                my_sessions = Session.fetch_by_user_id(user_id)
                if my_sessions:
                    sessions = sessions_schema.dump(my_sessions)

                    return {'sessions': sessions}, 200
                return {'message': 'No sessions found'}, 404
            return {'message': 'You are not authorised to view these sessions.'}, 403
        except Exception as e:
            print('========================================')
            print('error description: ', e)
            print('========================================')
            return {'message': 'Could not get user sessions.'}, 500
