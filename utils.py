import datetime
from functools import wraps
import flask
from flask import jsonify, app
import jwt
import conf


def authenticate_with_cookie_token(f):
    """Validates that token is correct for game & player, otherwise error"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Do something with your request here
        req = flask.request
        print(req.cookies)
        cookies = req.cookies.to_dict()
        print(cookies)
        player = cookies.get('player')
        gid = cookies.get('gid')
        token = cookies.get('token')
        print(gid)
        if not player or not gid or not token:
            flask.abort(401)
        data = jwt.decode(token, conf.secret_key, algorithms=["HS256"])
        if data.get('public_id') != player or data.get('gid') != gid:
            flask.abort(403)
        return f(*args, **kwargs)
    return decorated_function


def create_token(player_name, gid):
    return jwt.encode({'public_id': player_name, 'gid': gid, 'exp': datetime.datetime.now() + datetime.timedelta(minutes=120)},
                       conf.secret_key, algorithm="HS256")
