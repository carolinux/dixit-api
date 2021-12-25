import random
from uuid import uuid4

WAITING_TO_START = "waiting_to_start"
WAITING_FOR_NARRATOR = "waiting_for_narrator"
MIN_PLAYERS = 1 # for testing..
MAX_PLAYERS = 6
INITIAL_CARD_ALLOCATION = 6
SUBSEQUENT_CARD_ALLOCATION = 1

# TODO: state transitions...


class Game(object):

    def __init__(self, id=None):
        if id:
            self.id = id
        else:
            self.id = uuid4()
        self.sealedRounds = []
        self.currentState = WAITING_TO_START
        self.players = []
        self.narratorIdx = None
        self.cards = list(range(1, 71)) # change...



    def create_playing_order(self):
        random.shuffle(self.cards)
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

    def allocate_cards(self, card_allocation=SUBSEQUENT_CARD_ALLOCATION):
        self.currentRound['allocations'] = {}
        allocations = self.currentRound['allocations']
        for _ in range(card_allocation):
            for player in self.players:
                card = self.cards.pop()
                if player not in allocations:
                    allocations[player] = []
                allocations[player].append(card)


    def start(self):
        if self.is_started():
            raise Exception("Could not start game already in progress")
        elif len(self.players) < MIN_PLAYERS or len(self.players) > MAX_PLAYERS:
            raise Exception("Need to have between {} and {} players".format(MIN_PLAYERS, MAX_PLAYERS))
        else:
            #self.sealedStates.append(self.currentState)
            self.create_playing_order()
            self.narratorIdx = 0
            self.currentState = WAITING_FOR_NARRATOR
            self.currentRound = {}
            self.allocate_cards(INITIAL_CARD_ALLOCATION)
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

    def contains_player(self, player):
        return player in self.players

    def serialize_for_status_view(self, player):
        data = self.serialize_for_list_view()
        data['playerList'] = sorted([{"name": p} for p in self.players], key=lambda x: x['name'])
        data['roundInfo'] = self.get_round_info(player)
        data['isNarrator'] = self.get_narrator() == player
        return data


    def get_narrator(self):
        if self.narratorIdx:
            return self.players[self.narratorIdx]

    def get_round_info(self, player):
        if not self.is_started():
            return {'idx': None, 'narrator': None, 'cards': []}
        idx = len(self.sealedRounds) + 1
        phrase = self.currentRound.get('phrase')
        cards = self.currentRound.get('allocations', {}).get(player, [])
        return {'idx': idx, 'narrator': self.get_narrator(), 'phrase': phrase, 'cards': cards}