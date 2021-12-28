import datetime

import flask
from flask import Flask, request, jsonify, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin


from cute_ids import generate_cute_id
from models import Game
import utils
import conf

app = Flask(__name__)
app.config['SECRET_KEY'] = conf.secret_key
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
counter = {'c':0}


@socketio.on('connect')                                                         
def connect():      
  print('Client connected')                                                            
  emit('message', {'welcome': 'welcome'})


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

        try:
            game.join(player_name)
        except Exception as e:
            print(e)
            flask.abort(400, str(e))
        resp = make_response(jsonify({"game": game.id}))
        resp.set_cookie("player", player_name, domain='127.0.0.1')
        resp.set_cookie("gid", game.id)
        resp.set_cookie("token", utils.create_token(player_name, game.id))
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
    response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:3000"
    return response

def get_game_by_id(gid):
    return games.get(gid)

def add_game(g):
    games[g.id] = g


@app.route('/games/<gid>', methods=['POST', 'GET'])
@cross_origin()
@utils.authenticate_with_cookie_token
def games_status_api(gid):
    counter['c']+=1
    print("Called {} times".format(counter['c']))
    if request.method == "GET":

        ### verify that game exists and current request is allowed to get its general state and their personal data ###
        game, player = get_authenticated_game_and_player_or_error(gid, request)
        ### end verify ###

        game_data = game.serialize_for_status_view(player)
        # get the public state
        # TODO: and the users state, cards etc
        return jsonify({"game": game_data})


def get_authenticated_game_and_player_or_error(gid, request):
    intended_game = request.cookies.to_dict()['gid']
    player = request.cookies.to_dict()['player']
    if intended_game != gid:
        # the game in the cookie is different than the one the request is trying to get info for
        error = "Trying to get data for {} when the game the player is in is {}".format(gid, intended_game)
        print(error)
        flask.abort(403, error)
    game = get_game_by_id(gid)
    if not game:
        flask.abort(404)
    if not game.contains_player(player):
        error = "Player {} is not in game {}".format(player, gid)
        print(error)
        flask.abort(403, error)
    return game, player


def get_authenticated_game_and_player_or_error_for_resume(request):
    intended_game = request.cookies.to_dict()['gid']
    player = request.cookies.to_dict()['player']
    game = get_game_by_id(intended_game)
    if not game:
        flask.abort(404)
    if not game.contains_player(player):
        error = "Player {} is not in game {}".format(player, intended_game)
        print(error)
        flask.abort(403, error)
    return game, player



@app.route('/games/<gid>/start', methods=['PUT'])
@cross_origin()
@utils.authenticate_with_cookie_token
def games_start(gid):
    game, player = get_authenticated_game_and_player_or_error(gid, request)
    try:
        game.start()
    except Exception as e:
        print(e)
        flask.abort(400)
    game_data = game.serialize_for_status_view(player)
    return jsonify({"game": game_data})


@app.route('/games/<gid>/set', methods=['PUT'])
@cross_origin()
@utils.authenticate_with_cookie_token
def games_set_card(gid):
    game, player = get_authenticated_game_and_player_or_error(gid, request)
    try:
        card = request.json['card']
        phrase = request.json.get('phrase')
        if phrase:
            game.set_narrator_card(player, card, phrase)
        else:
            game.set_decoy_card(player, card)
    except Exception as e:
        print(e)
        flask.abort(400)
    game_data = game.serialize_for_status_view(player)
    return jsonify({"game": game_data})


@app.route('/games/<gid>/vote', methods=['PUT'])
@cross_origin()
@utils.authenticate_with_cookie_token
def games_vote_card(gid):
    game, player = get_authenticated_game_and_player_or_error(gid, request)
    try:
        card = request.json['vote'] # this is the 'string' of the card
        game.cast_vote(player, card)
    except Exception as e:
        print(e)
        flask.abort(400, str(e))
    game_data = game.serialize_for_status_view(player)
    return jsonify({"game": game_data})


@app.route('/games/<gid>/next', methods=['PUT'])
@cross_origin()
@utils.authenticate_with_cookie_token
def games_next_round(gid):
    game, player = get_authenticated_game_and_player_or_error(gid, request)
    try:
        game.start_next_round()
    except Exception as e:
        print(e)
        flask.abort(400, str(e))
    game_data = game.serialize_for_status_view(player)
    return jsonify({"game": game_data})


@app.route('/games/resume', methods=['GET'])
@cross_origin()
@utils.authenticate_with_cookie_token
def games_resume_from_cookie():
    game, player = get_authenticated_game_and_player_or_error_for_resume(request)
    return jsonify({"game": game.id, 'player': player})




if __name__ == '__main__':                                                      
  socketio.run(app, port=5000, debug=True) 
