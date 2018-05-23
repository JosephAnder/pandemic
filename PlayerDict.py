from collections import OrderedDict
from random import random


class PlayerDeck:
    deck = OrderedDict()
    discard = OrderedDict()

    def addCard(self, name, card):
        self.deck[name] = card

    def shuffle(self):
        shuffledList = sorted(self.deck.items(), key=lambda x: random())
        self.deck = OrderedDict(shuffledList)

    def addToDiscard(self, card):
        self.discard[card.initials] = card

    @staticmethod
    def indexToColor(num):
        if num == 0:
            return "blue"
        elif num == 1:
            return "yellow"
        elif num == 2:
            return "black"
        else:
            return "red"

    @staticmethod
    def colorToIndex(color):
        if color == "blue":
            return 0
        elif color == "yellow":
            return 1
        elif color == "black":
            return 2
        else:
            return 3

