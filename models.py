import random
from uuid import uuid4

WAITING_TO_START = "waiting_to_start"
WAIT_FOR_NARRATOR = "waiting_for_narrator"
MIN_PLAYERS = 3
MAX_PLAYERS = 6

# TODO: state transitions...


class Game(object):

    def __init__(self):
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

        if len(self.players) >= MAX_PLAYERS:
            raise Exception("Game {} is full".format(self.id))
        self.players.append(player_name)

        if len(self.players) == MAX_PLAYERS:
            self.start()

    def start(self):
        if self.currentState != WAITING_TO_START:
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
