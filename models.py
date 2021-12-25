import random
from uuid import uuid4

WAITING_TO_START = "waiting_to_start"
WAIT_FOR_NARRATOR = "waiting_for_narrator"
MIN_PLAYERS = 3
MAX_PLAYERS = 6

# TODO: state transitions...


class Game(object):

    def __init__(self, id=None):
        if id:
            self.id = id
        else:
            self.id = uuid4()
        self.sealedStates = []
        self.currentState = WAITING_TO_START
        self.players = []
        self.narratorIdx = None



    def create_playing_order(self):
        # can also use join order as playing order...
        random.shuffle(self.players)


    def rejoin(self, player_name):
        """rejoin game on disconnec"""
        return

    def join(self, player_name):
        if player_name in self.players:
            return

        if len(self.players) >= MAX_PLAYERS:
            raise Exception("Game {} is full".format(self.id))
        self.players.append(player_name)


    def is_started(self):
        return self.currentState != WAITING_TO_START

    def start(self):
        if self.is_started():
            raise Exception("Could not start game already in progress")
        elif len(self.players) < MIN_PLAYERS or len(self.players) > MAX_PLAYERS:
            raise Exception("Need to have between {} and {} players".format(MIN_PLAYERS, MAX_PLAYERS))
        else:
            #self.sealedStates.append(self.currentState)
            self.create_playing_order()
            self.narratorIdx = 0
            self.currentState = 'WAITING_FOR_NARRATOR'
            # notify non narrators
            # notify narrator in soquette

    def serialize_for_list_view(self, joinable_for_player=None):
        if not joinable_for_player:
            return {'id': self.id, 'players': len(self.players), 'state': self.currentState, 'playerString': ','.join(self.players)}
        else:
            return {'id': self.id, 'players': len(self.players), 'state': self.currentState,
                    'playerString': ','.join(self.players), 'join_action': self.get_joinability(joinable_for_player)}

    def get_joinability(self, player):

        if player in self.players:
            return 'rejoin' # and the player state is up to date with game state... i suppose
        elif len(self.players) < MAX_PLAYERS and not self.is_started():
            return 'join'
        else:
            return "game_already_started"

    def serialize_for_status_view(self):
        data = self.serialize_for_list_view()
        # TODO more state specific info
        return data