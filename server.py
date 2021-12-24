from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
from models import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config["DEBUG"] = True
socketio = SocketIO(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

games = {}

@socketio.on('connect')                                                         
def connect():      
  print('Client connected')                                                            
  emit('message', {'welcome': 'welcome'})



@app.route('/game', methods=['POST'])
@cross_origin()
def create_new_game():
    player_name = request.json['player']
    game = Game()
    games[game.id] = game
    game.join(player_name)
    return jsonify({"gameid": game.id})



if __name__ == '__main__':                                                      
  socketio.run(app, port=5000, debug=True) 
