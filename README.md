# dixit-api
The backend of a web app with that allows friends to play dixit online

# Rules & game logic

- 3-6 players
- At each round, there is a *main player*, who chooses a card and types a phrase.

# Endpoints

## /players

### Methods

- GET: Returns the information about all players.
- POST: Adds a new player

## /hasTurn

Returns if it is this player's turn as well as if this player is the main player:

`{ mainPlayer: true, hasTurn: false }`

## /cards?player=Foo

Returns a list with the cards of a certain player (by player name)

`[28, 66, 62, 63, 53, 41]`

## /initialCardsDistribution

Returns the initial cards distribution per player

## /start

Starts the game
