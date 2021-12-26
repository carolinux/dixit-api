import random
from uuid import uuid4

WAITING_TO_START = "waiting_to_start"
WAITING_FOR_NARRATOR = "waiting_for_narrator"
WAITING_FOR_PLAYERS = "waiting_for_players"
WAITING_FOR_VOTES = "waiting_for_votes"
ROUND_REVEALED = "round_revealed"
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
        self.cards = list(range(1, 101)) # <- for the medusa deck change... allow to choose deck?



    def create_playing_order(self):
        random.shuffle(self.cards)
        random.shuffle(self.players)


    def rejoin(self, player_name):
        """rejoin game on disconnec"""
        return


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
        data['isNarrator'] = self.is_narrator(player)
        return data


    def get_narrator(self):
        if self.narratorIdx is not None:
            return self.players[self.narratorIdx]

    def get_round_info(self, player):
        if not self.is_started():
            return {'idx': None, 'narrator': None, 'hand': [], 'playedCards': []}
        idx = len(self.sealedRounds) + 1
        phrase = self.currentRound.get('phrase')
        hand = self.currentRound.get('allocations', {}).get(player, [])
        played_cards = self.get_played_cards()
        return {'idx': idx, 'narrator': self.get_narrator(), 'phrase': phrase, 'hand': hand, 'playedCards': played_cards}

    def is_narrator(self, player):
        return self.get_narrator() == player

    def get_played_cards(self):
        #if self.currentState in (ROUND_REVEALED, WAITING_FOR_VOTES):
        # return more info
        if self.currentState == WAITING_FOR_PLAYERS:
            return (1 + len(self.currentRound['decoys'])) * ['back']
        return []




    ## state transitions from here on -- need to be locked ##

    def join(self, player_name):
        if player_name in self.players:
            return

        if len(self.players) >= MAX_PLAYERS:
            raise Exception("Game {} is full".format(self.id))
        self.players.append(player_name)

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
            self.currentRound['decoys'] = {}
            self.allocate_cards(INITIAL_CARD_ALLOCATION)


    def set_narrator_card(self, player, card, phrase):
        if not self.is_narrator(player):
            raise Exception("Trying to set card without being narrator {}, {}".format(player, self.get_narrator()))
        if self.currentState != WAITING_FOR_NARRATOR:
            raise Exception("Trying to set card at an invalid point in the game")
        self.currentRound['phrase'] = phrase
        self.currentRound['narratorCard'] = card
        self.currentRound['allocations'][player].remove(card)
        self.currentState = WAITING_FOR_PLAYERS


    def set_decoy_card(self, player, card):
        if self.is_narrator(player):
            raise Exception("Trying to set decoy card while being narrator")
        if self.currentState != WAITING_FOR_PLAYERS:
            raise Exception("Trying to set card at an invalid point in the game")

        self.currentRound['decoys'][player] = card
        self.currentRound['allocations'][player].remove(card)
        if len(self.currentRound['decoys'] == len(self.players) -1):
            self.currentState = WAITING_FOR_VOTES

