from flask import Flask, request, jsonify
# from flask_socketio import SocketIO, send
from flask_sse import sse

import random
from spec import UserAPI
import cryptocode
# from score import updateScore

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# app.config["REDIS_URL"] = "redis://localhost"
# app.register_blueprint(sse, url_prefix='/stream')

# Create server using socket and fix CORS errors
# socketIo = SocketIO(app, cors_allowed_origins='*')

app.debug = True
# app.host = 'localhost'

# Game constants
maxPlayersCount = 6
playersCount = 6
cardsPerPlayerCount = 6
enableVoting = False

players = [
  { 'name': 'Eleni', 'hasTurn': False  },
  { 'name': 'George', 'hasTurn': False },
  { 'name': 'Theodore', 'hasTurn': False }
]

# TODO: Encrypt players' names
playersDict = {}

cards = list(range(1, 70))
random.shuffle(cards)
playedCards = { 'cards': [], 'phrase': '', 'enableVoting': enableVoting }

# @socketIo.on('cardSelected')
# def handle_card_selection(card):
#   print('Received***', card)

#   # send(card, broadcast=True)
#   return None

# @socketIo.on('phraseSelected')
# def handle_phrase_selection(phrase):
#   print('Phrase***:', phrase)
#   send(phrase, broadcast=True)
#   return None

for player in players:
  player['cards'] = cards[0:cardsPerPlayerCount]
  del cards[:cardsPerPlayerCount]

# Manage players
@app.route('/players', methods=['GET', 'POST'])
def manage_players():
  if request.method == 'GET':
    sse.publish({"message": 'foo'}, type='publish')
    return jsonify(players)
  elif request.method == 'POST':
    name = request.json['player']
    player = { 'name': name, 'hasTurn': False, 'mainPlayer': False }
    encodedName = cryptocode.encrypt(name, 'foo')
    print(encodedName)
    if len(players)<maxPlayersCount:
      players.append(player)
    return jsonify(players)

# Play card
@app.route('/playedCards', methods=['POST', 'GET'])
def play_card():
  if request.method=='POST':
    print('posting')
    mainPlayer = request.json['mainPlayer']
    card = request.json['card']
    playedCards['cards'].append(card)
    if mainPlayer==True:
      phrase = request.json['phrase']
      playedCards['phrase'] = phrase
    
    # TODO: Shuffle
    # random.shuffle(playedCards)
    
    if len(playedCards['cards']) == playersCount:
      enableVoting = True
    else:
      enableVoting = False
    playedCards['enableVoting'] = enableVoting
    # send('phraseSelected', broadcast=True)
    return jsonify(playedCards)
  
  if request.method=='GET':
    return jsonify(playedCards)

# Add new player
@app.route('/start', methods=['POST'])
def start_game():
  random.shuffle(players)
  players[0]['hasTurn'] = True
  return jsonify(players)

# Shuffle cards & return their distribution per player
@app.route('/initialCardsDistribution')
def distribute_cards():
  return players

# Return cards of a player
@app.route('/cards', methods=['GET'])
def return_cards_per_player():
  cards = []
  playerName = request.args.get('player')
  for player in players:
    if player['name'] == playerName:
      cards = player['cards']   
    
  return jsonify(cards)

# Return true if it is this player's turn, false otherwise
@app.route('/hasTurn', methods=['GET'])
def return_player_turn():
  # TODO: Implement logic
  return jsonify({
    'mainPlayer': True,
    'hasTurn': True
  })

# Calculate what should happen at the end of each round
# & return the next player (if the game has not finished)
@app.route('/roundCompleted', methods=['POST'])
def complete_round():
  # print(updateScore([]))
 
  # Calculate next player
  players[0]['hasTurn'] = False
  players.append(players[0])
  players.pop(0)
  players[0]['hasTurn'] = True
  return jsonify(players)
  # TODO:
  # 1. Calculate & update scores
  # 2. Check if maximum score was reached
  #   2a. If yes: finish the game:
  #       - Return: { gameFinished: true, scores } 
  #   2b. If no:
  #       - Calculate next player's turn
  #       - Update the db with the last player that played
  #       - Trash used cards
  #       - Give a new card to each player
  #       - Return: { gameFinished: false, scores, currentPlayer }
  
  # res = jsonify({ 'gameFinished': False, 'scores': [], 'currentPlayer': 1 })
  # return res

if __name__ == '__main__':
  # socketIo.run(app)
  app.run()


