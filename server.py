from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import random
from spec import UserAPI
# import cryptocode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config["DEBUG"] = True
socketio = SocketIO(app)                                                        

# Game constants
maxPlayersCount = 6
cardsPerPlayerCount = 6

players = [
  { 'name': 'Eleni', 'hasTurn': True  },
  { 'name': 'George', 'hasTurn': False },
  { 'name': 'Theodore', 'hasTurn': False }
]

# TODO: Encrypt players' names
playersDict = {}

cards = list(range(1, 70))
playedCards = { 'cards': [], 'phrase': '' }
random.shuffle(cards)

for player in players:
  player['cards'] = cards[0:cardsPerPlayerCount]
  del cards[:cardsPerPlayerCount]


@socketio.on('connect')                                                         
def connect():      
  print('Client connected')                                                            
  emit('message', {'welcome': 'welcome'})  

# Manage players
@app.route('/players', methods=['GET', 'POST'])
def manage_players():
  if request.method == 'GET':
    return jsonify(players)
  elif request.method == 'POST':
    name = request.json['player']
    player = { 'name': name, 'hasTurn': False, 'mainPlayer': False }

    if len(players)<maxPlayersCount:
      players.append(player)
    return jsonify(players)

# Play card
@app.route('/playedCards', methods=['POST', 'GET'])
def play_card():
  if request.method=='POST':
    if len(players) > len(playedCards['cards']):
      card = request.json['card']
      mainPlayer = request.json['mainPlayer']
      playedCards['cards'].append(card)

      if mainPlayer:
        phrase = request.json['phrase']
        playedCards['phrase'] = phrase

      # If all players have played, notify clients
      # that all players played and the turn was completed
      if len(players) == len(playedCards['cards']):
        roundCompleted = True
        # Send notification via web sockets, add extra info
        # emit('message', roundCompleted)
      else:
        roundCompleted = False
    else:
      roundCompleted = True

   # TODO: [improvement] cards played could be encrypted so that other players cannot see them (in the response)
    random.shuffle(playedCards['cards'])
    roundInfo = jsonify({
      'playerPlayed': True,
      'roundCompleted': roundCompleted,
      'phrase': playedCards['phrase'],
      'cards': playedCards['cards']
    })
    return roundInfo

  if request.method=='GET':
    if len(players) > len(playedCards['cards']):
      roundCompleted = False
    else:
      roundCompleted = True

    random.shuffle(playedCards['cards'])
    roundInfo = jsonify({
      'playerPlayed': False,
      'roundCompleted': roundCompleted,
      'phrase': playedCards['phrase'],
      'cards': playedCards['cards']
    })
    return roundInfo

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
  
# app.run()


if __name__ == '__main__':                                                      
    socketio.run(app, debug=True) 
