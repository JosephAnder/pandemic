import Cities as citiesCollection
import InfectDict
import PlayerDict
from collections import OrderedDict

cities = citiesCollection.cities
infectDeck = InfectDict.InfectDeck()
playerDeck = PlayerDict.PlayerDeck()


class Card:
    def __init__(self, initials, name, color):
        self.initials = initials
        self.name = name
        self.color = color

    def __str__(self):
        return self.name + " " + self.color

    def __len__(self):
        return len(self.name)

    def getBackgroundColor(self):
        if self.color == "blue":
            return "#0099ff"
        elif self.color == "yellow":
            return "#ffcc00"
        elif self.color == "red":
            return "#ff5050"
        elif self.color == "black":
            return "#8585ad"
        elif self.color == "gold":
            return "#e69900"

for cityInitials, city in cities.items():
    tempInfectCard = Card(cityInitials, city.name, city.color)
    tempPlayerCard = Card(cityInitials, city.name, city.color)
    infectDeck.addCard(cityInitials, tempInfectCard)
    playerDeck.addCard(cityInitials, tempPlayerCard)

tempPlayerCard = Card("Qn", "Quiet Night", "gold")
playerDeck.addCard("Qn", tempPlayerCard)
tempPlayerCard = Card("Air", "Airlift", "gold")
playerDeck.addCard("Air", tempPlayerCard)
tempPlayerCard = Card("Cr", "City Resist", "gold")
playerDeck.addCard("Cr", tempPlayerCard)
tempPlayerCard = Card("Tb", "Travel Ban", "gold")
playerDeck.addCard("Tb", tempPlayerCard)
tempPlayerCard = Card("Rg", "Research Grant", "gold")
playerDeck.addCard("Rg", tempPlayerCard)

