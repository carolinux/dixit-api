from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin

from cute_ids import generate_cute_id
from models import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config["DEBUG"] = True
socketio = SocketIO(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

games = {}
games['chonky-bird'] = Game('chonky-bird')

@socketio.on('connect')                                                         
def connect():      
  print('Client connected')                                                            
  emit('message', {'welcome': 'welcome'})



@app.route('/games', methods=['POST', 'GET'])
@cross_origin()
def games_api():
    if request.method == 'POST':
        player_name = request.json['player']
        while True:
            uid = generate_cute_id()
            if uid not in games:
                break
        game = Game(uid)
        games[game.id] = game
        game.join(player_name)
        return jsonify({"gameid": game.id})

    else:
        if request.args.get('joinable_for_player'):
            player = request.args.get('joinable_for_player')
        else:
            player = None
        return jsonify({"games": [g.serialize_for_list_view(joinable_for_player=player) for _, g in games.items()]})

if __name__ == '__main__':                                                      
  socketio.run(app, port=5000, debug=True) 
