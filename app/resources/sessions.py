from datetime import timedelta

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask import abort, jsonify

from models.session_model import Session, SessionSchema

api = Namespace('session', description='View User Sessions')

session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)


@api.route('')
class SessionList(Resource):
    @api.doc('list_user_sessions')
    @jwt_required
    def get(self):
        '''List User Sessions'''
        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        if authorised_user['privileges'] == 'Customer care' or claims['is_admin'] :
            my_sessions = Session.fetch_all()
            sessions = sessions_schema.dump(my_sessions)
            return {'status': 'Matches retrieved', 'sessions': sessions}, 200
        user_id = authorised_user['id']
        my_sessions = Session.fetch_by_user_id(user_id)
        sessions = sessions_schema.dump(my_sessions)
        return {'status': 'Matches retrieved', 'sessions': sessions}, 200
