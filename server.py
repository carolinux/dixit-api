from flask import Flask
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

# Shuffle cards & distribute them per player
@app.route('/initialCardsDistribution')
def distribute_cards():
  random.shuffle(cards)
  cardsPerPlayer = {}

  for player in players:
    cardsPerPlayer[player] = cards[0:6]
    del cards[:6]
  return cardsPerPlayer

app.run()


# @app.route('/', methods=['GET'])