from collections import OrderedDict
from random import random
import Cities as citiesCollection
import Card as cardCollection
from PlayerChar import Player

cities = citiesCollection.cities
infectDeck = cardCollection.infectDeck
playerDeck = cardCollection.playerDeck
players = []

cheatingMode = False
playerCount = 4
epidemicCards = 4

def getPlayerIndex(color):
    for playerIndex, player in enumerate(players):
        if color == player.color:
            return playerIndex
    return -1

for x in range(0, 5):
    infectDeck.shuffle()
    playerDeck.shuffle()

colors = ["Brown", "DarkGreen", "LightGreen", "Orange", "White"] #"Pink", "Blue"
colors = sorted(colors, key=lambda rand: random())

for x in range(0, playerCount):
    color = colors.pop(0)
    players.append(Player(x, color))
    colors = sorted(colors, key=lambda rand: random())

#2p 4 cards
#3p 3 cards
if not cheatingMode:
    for player in players:
        for x in range(0, 6 - playerCount):
            tempPlayerCard = playerDeck.deck.popitem(last=False)
            player.addCard(tempPlayerCard[1])
else:
    cardsToAdd = []
    for playerIndex, player in enumerate(players):
        color = "blue"
        if playerIndex == 0:
            color = "blue"
        elif playerIndex == 1:
            color = "yellow"
        elif playerIndex == 2:
            color = "black"
        else:
            color = "red"
        while len(player.hand) < 7:
            tempPlayerCard = playerDeck.deck.popitem(last=False)
            if tempPlayerCard[1].color == color:
                player.addCard(tempPlayerCard[1])
            else:
                cardsToAdd.append(tempPlayerCard)
        for card in cardsToAdd:
            playerDeck.addCard(card[0], card[1])

# Add 4 epidemic cards
deckLength = len(playerDeck.deck)
subDecks = []
for x in range(0, epidemicCards):
    tempDeck = OrderedDict()
    subDecks.append(tempDeck)
while playerDeck.deck:
    for count in range(0, epidemicCards):
        if not playerDeck.deck:
            break
        tempPlayerCard = playerDeck.deck.popitem(last=False)
        subDecks[count%4][tempPlayerCard[1].name] = tempPlayerCard[1]
for index in range(0, epidemicCards):
    tempEpidemicCard = cardCollection.Card("Ep" + str(index), "Epidemic " + str(index + 1), "green")
    subDecks[index]["Ep" + str(index)] = tempEpidemicCard
    subDecks[index] = OrderedDict(sorted(subDecks[index].items(), key=lambda rand: random()))
for x in range(0, epidemicCards):
    while subDecks[x]:
        tempPlayerCard = subDecks[x].popitem(last=False)
        playerDeck.addCard(tempPlayerCard[1].name, tempPlayerCard[1])

blackList = []
darkGreenIndex = getPlayerIndex("DarkGreen")
if darkGreenIndex >= 0:
    blackList.append(cities[players[darkGreenIndex].city].name)
    for blackListCity in cities[players[darkGreenIndex].city].neighbors:
        blackList.append(cities[blackListCity].name)
for x in range(0, 9):
    cityInitials = infectDeck.draw()
    cities[cityInitials].infect(cities[cityInitials].color, x%3+1, blackList)
cities["At"].addRS()





