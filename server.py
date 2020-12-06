from flask import Flask, request, jsonify
# from flask.ext.socketio import SocketIO, emit
import random
# from score import updateScore

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)
app.config["DEBUG"] = True

# Game constants
maxPlayersCount = 6
cardsPerPlayerCount = 6

players = [
  { 'name': 'Eleni', 'hasTurn': False  },
  { 'name': 'George', 'hasTurn': False },
  { 'name': 'Theodore', 'hasTurn': False }
]

cards = list(range(1, 70))
playedCards = { 'cards': [], 'phrase': '' }
random.shuffle(cards)

for player in players:
  player['cards'] = cards[0:cardsPerPlayerCount]
  del cards[:cardsPerPlayerCount]

# @socketio.on('my event')                          # Decorator to catch an event called "my event":
# def test_message(message):                        # test_message() is the event callback function.
#   emit('my response', {'data': 'got it!'})        # Trigger a new event called "my response" 


# Return players
@app.route('/players', methods=['GET'])
def return_players():
  return jsonify(players)

# Add new player
@app.route('/players', methods=['POST'])
def add_player():
  player = { 'name': request.json['player'], 'hasTurn': False }
  if len(players)<maxPlayersCount:
    players.append(player)
  return jsonify(players)

# Play card
@app.route('/playedCards', methods=['POST', 'GET'])
def play_card():
  # TODO: To fix condition about number of players (does not work)
  if request.method=='POST' and len(players) > len(playedCards):
    card = request.json['card']
    phrase = request.json['phrase']
    playedCards['cards'].append(card)
    playedCards['phrase'] = phrase
    
    # TODO: Shuffle
    # random.shuffle(playedCards)
    
    # if len(playedCards)==len(players):
      # send a notification to the client...

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
  return jsonify({'hasTurn': True})

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
  
  res = jsonify({ 'gameFinished': False, 'scores': [], 'currentPlayer': 1 })
  return res

app.run()

