import datetime

import jwt
from flask import Flask, request, jsonify, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin


from cute_ids import generate_cute_id
from models import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'verysecret!'
app.config["DEBUG"] = True
socketio = SocketIO(app)
cors = CORS(app)
# origins=["http://127.0.0.1:3000"], headers=['Content-Type'], expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
app.config['CORS_SUPPORTS_CREDENTIALS'] = True
app.config['CORS_ORIGINS'] = ["http://127.0.0.1:3000"]
app.config['CORS_EXPOSE_HEADERS'] = ['Access-Control-Allow-Origin']

games = {}
games['chonky-bird'] = Game('chonky-bird')


@socketio.on('connect')                                                         
def connect():      
  print('Client connected')                                                            
  emit('message', {'welcome': 'welcome'})


def create_token(player_name, gid):
    return jwt.encode({'public_id': player_name, 'gid': gid, 'exp': datetime.datetime.now() + datetime.timedelta(minutes=120)},
                       app.config['SECRET_KEY'])

@app.route('/cookie/')
def cookie():
    res = make_response("Setting a cookie")
    res.set_cookie('foog', 'bar')
    res.set_cookie('whar', 'garbl')
    print(res.headers)
    return res


@app.route('/games', methods=['POST', 'GET'])
@cross_origin()
def games_api():
    if request.method == 'POST':
        player_name = request.json['player']
        game_id = request.json["game"]
        if game_id == "new":
            while True:
                uid = generate_cute_id()
                if uid not in games:
                    break
            game = Game(uid)
            add_game(game)
        else:
            uid = game_id
            game = get_game_by_id(uid)

        game.join(player_name)
        resp = make_response(jsonify({"game": game.id}))
        resp.set_cookie("player", player_name, domain='127.0.0.1')
        resp.set_cookie("gid", game.id)
        resp.set_cookie("token", create_token(player_name, game.id))
        print(resp.headers)
        return resp

    else:
        if request.args.get('joinable_for_player'):
            player = request.args.get('joinable_for_player')
        else:
            player = None
        return jsonify({"games": [g.serialize_for_list_view(joinable_for_player=player) for _, g in games.items()]})


@app.after_request
def creds(response):
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

def get_game_by_id(gid):
    return games[gid]


def add_game(g):
    games[g.id] = g


@app.route('/games/<gid>', methods=['POST', 'GET'])
@cross_origin()
def games_status_api(gid):
    if request.method == "GET":
        player_name = request.args.get('player')
        game = get_game_by_id(gid)
        game_data = game.serialize_for_status_view()
        # get the public state
        # and the users state TODO: verify user id with JWT..
        return jsonify({"game": game_data})


if __name__ == '__main__':                                                      
  socketio.run(app, port=5000, debug=True) 
