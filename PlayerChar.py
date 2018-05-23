from collections import OrderedDict
import Cities as citiesCollection
import Card as cardCollection

cities = citiesCollection.cities
playerDeck = cardCollection.playerDeck

class Player:
    def __init__(self, number, color, city="At"):
        self.number = number
        self.color = color
        self.city = city
        self.role, self.line1, self.line2 = self.getText()
        self.hand = OrderedDict()
        self.handFull = False
    def showHand(self):
        return self.hand.items()
    def addCard(self, card):
        #if len(self.hand.items()) < 7:
        self.hand[card.initials] = card
        if card.initials in playerDeck.discard:
            playerDeck.discard.pop(card.initials)
        #else:
        if len(self.hand.items()) > 7:
            #playerDeck.discard[card.initials] = card
            self.handFull = True
    def removeCard(self, name):
        self.hand.move_to_end(name)
        card = self.hand.popitem()
        playerDeck.discard[card[1].initials] = card[1]
        return card
    def getCard(self, name):
        self.hand.move_to_end(name)
        card = self.hand.popitem()[1]
        self.addCard(card)
        return card
    def getMoves(self):
        moves = []
        for neighbor in cities[self.city].neighbors:
            moves.append(neighbor)
        return moves
    def moveTo(self, city):
        self.city = city
    def getText(self):
        if self.color == "Blue" or self.color == "Pink":
            pass
        elif self.color == "White":
            return "Scientist", "Cures only take 4 cards", None
        elif self.color == "Orange":
            return "Medic", "Treat: Remove all cubes", "Auto: Remove cubes of cured colors in your city"
        elif self.color == "DarkGreen":
            return "Quarantine Specialist", "Prevent cube placements in nearby cities", None
        elif self.color == "LightGreen":
            return "Operations Expert", "Make a Research Station: No discard required", "Discard: Move to any Research Station"
        elif self.color == "Brown":
            return "Researcher", "Share Knowledge: Give any city card", "Players may take any card from this player"
        return None, None

