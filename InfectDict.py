from collections import OrderedDict
from random import random


class InfectDeck:
    deck = OrderedDict()
    discard = OrderedDict()

    def addCard(self, name, card):
        self.deck[name] = card

    def shuffle(self):
        self.deck = OrderedDict(sorted(self.deck.items(), key=lambda x: random()))

    def draw(self, bottom=False):
        tempCard = self.deck.popitem(last=bottom)
        self.discard[tempCard[0]] = tempCard[1]
        return str(tempCard[0])

    def intensify(self):
        shuffledList = sorted(self.discard.items(), key=lambda x: random())
        shuffledList = sorted(shuffledList, key=lambda x: random())
        shuffledList = sorted(shuffledList, key=lambda x: random())
        self.discard = OrderedDict(shuffledList)
        for x in range(0, len(self.deck)):
            tempCard = self.deck.popitem()
            self.discard[tempCard[0]] = tempCard[1]
        self.deck = OrderedDict(self.discard)
        self.discard = OrderedDict()

    def getItems(self):
        return self.deck.items()

    def removeFromDiscard(self, card):
        self.discard.move_to_end(card.initials)
        self.discard.popitem()

