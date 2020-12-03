from flask import Flask, jsonify
import random

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def index():
  return 'Server Works!'

@app.route('/greet')
def say_hello():
  return 'Hello from Server'

cards = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
players = ['Eleni', 'George', 'Theodore']

# Shuffles cards & returns their distribution per player
@app.route('/initialCardsDistribution')
def distribute_cards():
  random.shuffle(cards)
  cardsPerPlayer = {}

  for player in players:
    cardsPerPlayer[player] = cards[0:6]
    del cards[:6]
  return cardsPerPlayer

# Returns true if it is this player's turn, false otherwise
@app.route('/hasTurn', methods=['GET'])
def return_player_turn():
  # TODO: Implement logic
  return jsonify({'hasTurn': True})

# Calculates what should happen at the end of each round
# & returns next player (if the game has not finished)
@app.route('/roundCompleted', methods=['POST'])
def complete_round():
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

