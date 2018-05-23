import subprocess
import sys
from functools import partial

from PIL.ImageQt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import Card as cardCollection
import Cities as citiesCollection
import Setup
from ActionItem import Action

cities = citiesCollection.cities
infectDeck = cardCollection.infectDeck
playerDeck = cardCollection.playerDeck
players = Setup.players
playerCount = Setup.playerCount


# noinspection PyCallByClass
def imageToPixmap(name):
    im = Image.open('imgs/' + name)
    image = ImageQt(im)
    return QPixmap.fromImage(image)

class App(QWidget):
    def __init__(self):
        super().__init__()
        #Graphic Items
        self.title = "Pandemic"
        self.width = 1920
        self.height = 1080
        self.font = QFont()
        self.font.setPixelSize(14)
        self.pixmap = QPixmap('imgs/makeMapDarker.png')
        self.closeButton = QPushButton("X", self)
        self.moveLabel = QLabel(self)
        self.actionLabel = QLabel("Other Actions:", self)
        self.specialLabel = QLabel("Player Ability Actions:", self)
        self.cureBackgroundLabel = QLabel(self)
        self.cureTextLabel = QLabel("Cures:", self)
        self.cubes = []
        self.rs = []
        self.cubeCount = [0, 0, 0, 0]
        self.cures = [False, False, False, False]
        self.eradicated = [False, False, False, False]
        self.rsLocations = ["At"]
        self.playerLabels = []
        self.handLabels = []
        self.backgroundLabels = []
        self.handButtons = []
        self.moveButtons = []
        self.rowOneButtonIndex = 0
        self.currentPlayer = 0
        self.currentInfectionRate = 0
        self.infectionRates = [2, 2, 2, 3, 3, 4, 4]
        self.outbreakCounter = 0
        self.currentMoves = []
        self.cureLabels = []
        self.infectDiscardLabel = QLabel("Infect Discard:", self)
        self.playerDiscardLabel = QLabel("Player Discard:", self)
        self.textBoxes = []
        self.cityLabels = dict()
        self.currentlyMoving = False
        self.goToRS = False
        self.rsCard = None
        self.winner = False
        self.loser = False
        #Event Items
        self.quietNight = False
        self.cityResist = False
        self.travelBan = (False, -1)
        self.researchGrant = False
        self.canUndo = True

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        font = QFont()
        font.setPixelSize(12)
        self.setFont(font)

        self.moveLabel.move(10, self.pixmap.height() + 10)
        self.actionLabel.move(10, self.pixmap.height() + 65)
        self.specialLabel.move(10, self.pixmap.height() + 125)
        for index in range(0, playerCount):
            self.backgroundLabels.append(QLabel(self))
            self.backgroundLabels[index].setStyleSheet("background-color: " + self.colorToHex(players[index].color))
            self.backgroundLabels[index].setGeometry(QRect(self.pixmap.width(), (index * 150) - 3, self.width - self.pixmap.width(), 148))
            self.handLabels.append(QLabel("Player " + str(index + 1) + " (" + players[index].role + "):", self))
            self.handLabels[index].move(self.pixmap.width() + 5, (index * 150) + 3)
            descriptionLabel = QLabel(players[index].line1, self)
            descriptionLabel.move(self.pixmap.width() + 10, self.handLabels[index].y() + 20)
            descriptionLabel = QLabel(players[index].line2, self)
            descriptionLabel.move(self.pixmap.width() + 10, self.handLabels[index].y() + 35)
        self.infectDiscardLabel.move(self.pixmap.width() + 5, self.backgroundLabels[-1].y() + 180)
        self.playerDiscardLabel.move(self.pixmap.width() + self.backgroundLabels[-1].width() / 2 + 5, self.backgroundLabels[-1].y() + 180)

        self.cureBackgroundLabel.setStyleSheet("background-color: #2eb8b8")
        self.cureBackgroundLabel.setGeometry(QRect(self.pixmap.width() / 4, self.pixmap.height() - 80, 250, 80))
        self.cureTextLabel.move(self.pixmap.width() / 4 + 10, self.pixmap.height() - 75)
        self.setFixedSize(self.width, self.height)

        self.closeButton.move(self.pixmap.width() - 35, 5)
        self.closeButton.setStyleSheet("background-color: #ff6666")
        self.closeButton.resize(30, 30)
        self.closeButton.clicked.connect(self.close)
        self.closeButton.show()

        self.updateMap()

    @staticmethod
    def colorToHex(color):
        if color == "Blue":
            return "#00b8e6"
        elif color == "Brown":
            return "#bf8040"
        elif color == "DarkGreen":
            return "#2d862d"
        elif color == "LightGreen":
            return "#77b300"
        elif color == "Orange":
            return "#ff751a"
        elif color == "Pink":
            return "#ff99e6"
        elif color == "White":
            return "#fefefe"

    @staticmethod
    def colorToIndex(color):
        if color == "blue":
            return 0
        elif color == "yellow":
            return 1
        elif color == "black":
            return 2
        elif color == "red":
            return 3

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


    def makeCube(self, color, x, y):
        cubeLabel = QLabel(self)
        self.cubes.append(cubeLabel)
        cubeLabel.setPixmap(imageToPixmap(color + "Cube.png"))
        cubeLabel.move(x, y)
        cubeLabel.setScaledContents(True)
        cubeLabel.resize(20, 20)
        cubeLabel.show()

    def drawRS(self, x, y):
        rsLabel = QLabel(self)
        self.rs.append(rsLabel)
        rsLabel.setPixmap(QPixmap('imgs/rs.png'))
        rsLabel.move(x, y)
        rsLabel.setScaledContents(True)
        rsLabel.resize(25, 20)
        rsLabel.show()

    def drawPlayer(self, color, x, y):
        playerLabel = QLabel(self)
        self.playerLabels.append(playerLabel)
        playerLabel.setPixmap(imageToPixmap("player" + color + ".png"))
        playerLabel.move(x, y)
        playerLabel.setScaledContents(True)
        playerLabel.resize(15, 20)
        playerLabel.show()

    def drawHand(self, playerIndex):
        xIndex = 0
        nextRow = False
        for name, card in players[playerIndex].showHand():
            if xIndex > 3:
                xIndex = 0
                nextRow = True
            handButton = QPushButton(card.name, self)
            self.handButtons.append(handButton)
            if not nextRow:
                handButton.move(self.handLabels[playerIndex].x()+xIndex * 68, self.handLabels[playerIndex].y() + 60)
            else:
                handButton.move(self.handLabels[playerIndex].x() + xIndex * 68, self.handLabels[playerIndex].y() + 90)
            handButton.resize(68, 27)
            handButton.clicked.connect(partial(self.discard, players[playerIndex], card))
            handFont = QFont()
            if len(card) > 15:
                handFont.setPixelSize(24 - len(card))
            elif len(card) > 13:
                handFont.setPixelSize(23 - len(card))
            elif len(card) > 12:
                handFont.setPixelSize(22 - len(card))
            else:
                handFont.setPixelSize(21 - len(card))
            handButton.setStyleSheet("background-color: " + card.getBackgroundColor())
            handButton.setFont(handFont)
            handButton.show()
            xIndex = xIndex + 1
            if nextRow and xIndex == 3:
                return

    def makeMoveButton(self, action, text, x, y, fontSize=12, color=None, width=115, height=32):
        moveButton = QPushButton(text, self)
        self.moveButtons.append(moveButton)
        moveButton.move(x, y)
        moveButton.resize(width, height)
        if action:
            moveButton.clicked.connect(action)
        font = QFont()
        font.setPixelSize(fontSize)
        if isinstance(color, str):
            moveButton.setStyleSheet("background-color: " + color)
        moveButton.setFont(font)
        moveButton.show()

    def drawMap(self):
        self.cubeCount = [0, 0, 0, 0]
        for index, cityInitials in enumerate(cities):
            cityLabel = QLabel(self)
            cityLabel.setText(" " + cities[cityInitials].name + " ")

            cityLabel.setStyleSheet("background-color:" + cities[cityInitials].getColor() + "; color: black")
            cityLabel.setFont(self.font)
            cityLabel.move(cities[cityInitials].posX, cities[cityInitials].posY)
            colors = cities[cityInitials].getCubes()
            if cities[cityInitials].cubeCount >= 1:
                colorIndex = cities[cityInitials].colorToIndex(colors[0])
                self.cubeCount[colorIndex] = self.cubeCount[colorIndex] + 1
                self.makeCube(colors[0], cities[cityInitials].posX, cities[cityInitials].posY+18)
            if cities[cityInitials].cubeCount >= 2:
                colorIndex = cities[cityInitials].colorToIndex(colors[0])
                self.cubeCount[colorIndex] = self.cubeCount[colorIndex] + 1
                self.makeCube(colors[1], cities[cityInitials].posX + 18, cities[cityInitials].posY + 18)
            if cities[cityInitials].cubeCount == 3:
                colorIndex = cities[cityInitials].colorToIndex(colors[0])
                self.cubeCount[colorIndex] = self.cubeCount[colorIndex] + 1
                self.makeCube(colors[2], cities[cityInitials].posX + 36, cities[cityInitials].posY + 18)
            if cities[cityInitials].rs:
                self.drawRS(cities[cityInitials].posX-27, cities[cityInitials].posY)
            self.cityLabels[cityInitials] = cityLabel
            cityLabel.show()

        infectRate = self.infectionRates[self.currentInfectionRate]
        if self.travelBan[0]:
            infectRate = 1
        infectionRate = QLabel("Infection Rate: " + str(infectRate), self)
        infectionRate.move(self.pixmap.width() + 5, self.backgroundLabels[-1].y() + 155)
        infectionRate.show()
        self.textBoxes.append(infectionRate)

        outbreakCounter = QLabel("Outbreaks: " + str(self.outbreakCounter), self)
        outbreakCounter.move(self.pixmap.width() + self.backgroundLabels[-1].width() / 2 + 5, self.backgroundLabels[-1].y() + 155)
        outbreakCounter.show()
        self.textBoxes.append(outbreakCounter)

        infectDiscard = QTextBrowser(self)
        infectDiscard.setGeometry(QRect(self.pixmap.width() + 5, self.infectDiscardLabel.y() + 15,
                                        self.backgroundLabels[-1].width() / 2 - 10, 157))
        for name, card in infectDeck.discard.items():
            infectDiscard.append(card.name + " (" + card.color + ")")
        infectDiscard.show()
        self.textBoxes.append(infectDiscard)

        playerDiscard = QTextBrowser(self)
        playerDiscard.setGeometry(QRect(self.pixmap.width() + self.backgroundLabels[-1].width() / 2 + 5, self.playerDiscardLabel.y() + 15,
                                        self.backgroundLabels[-1].width() / 2 - 10, 157))
        for name, card in playerDeck.discard.items():
            playerDiscard.append(card.name + " (" + card.color + ")")
        playerDiscard.show()
        self.textBoxes.append(playerDiscard)

        for cureIndex, cure in enumerate(self.cures):
            pixmapString = None
            if self.eradicated[cureIndex]:
                pixmapString = self.indexToColor(cureIndex) + "Eradicated.png"
            elif cure:
                pixmapString = self.indexToColor(cureIndex) + "Cure.png"
            if pixmapString:
                cureLabel = QLabel(self)
                cureLabel.setPixmap(imageToPixmap(pixmapString))
                cureLabel.move(self.cureBackgroundLabel.x() + (60 * cureIndex) + 10, self.pixmap.height() - 55)
                cureLabel.setScaledContents(True)
                cureLabel.resize(50, 50)
                cureLabel.show()
                self.cureLabels.append(cureLabel)

        undoButton = QPushButton("Undo", self)
        undoButton.clicked.connect(self.undo)
        undoButton.move(self.pixmap.width() + 10, self.pixmap.height() + 20)
        undoButton.setStyleSheet("font-size: 20pt; background-color: #b3ccff")
        undoButton.resize(self.width - self.pixmap.width() - 20, 50)

        turnButton = QPushButton("End Turn", self)
        turnButton.clicked.connect(self.endTurn)
        turnButton.move(self.pixmap.width() + 10, self.pixmap.height() + 80)
        turnButton.setStyleSheet("font-size: 20pt; background-color: #b3ffcc")
        turnButton.resize(self.width - self.pixmap.width() - 20,  50)

        restartButton = QPushButton("Restart", self)
        restartButton.clicked.connect(self.restart)
        restartButton.move(self.pixmap.width() + 10, self.pixmap.height() + 140)
        restartButton.setStyleSheet("font-size: 20pt; background-color: #ff9999")
        restartButton.resize(self.width - self.pixmap.width() - 20, 50)

    def drawPlayers(self):
        if players[self.currentPlayer-1].handFull:
            self.moveLabel.setText("Player " + str(players[self.currentPlayer-1].number + 1) + ": Your hand is full, discard till you have 7 cards")
        else:
            self.moveLabel.setText("Player " + str(self.currentPlayer + 1) + " (" + players[self.currentPlayer].color + ") Moves:")
        self.moveLabel.adjustSize()
        for index, player in enumerate(players):
            self.drawPlayer(player.color, cities[player.city].posX + index * 20, cities[player.city].posY - 20)
            self.drawHand(index)

    def drawMoves(self):
        self.playerDiscardLabel.setText("Player Discard: " + str(len(playerDeck.deck)) + " left")
        self.playerDiscardLabel.show()
        if self.winner:
            theFontForWinners = QFont("Unispace", 32)
            theTextForWinners = " Wow, You Won! "
            if Setup.cheatingMode:
                theTextForWinners = " Wow, You Won Cheater! "
            winLabel = QLabel(theTextForWinners, self)
            winLabel.setFont(theFontForWinners)
            winLabel.setStyleSheet("background-color: #80aaff")
            winLabel.move(self.pixmap.width() / 2 - 150, 600)
            winLabel.show()
        elif self.loser:
            theFontForEveryoneElse = QFont("Comic Sans MS", 32)
            normalLabel = QLabel(" Sorry not sorry, you lost. ", self)
            normalLabel.setFont(theFontForEveryoneElse)
            normalLabel.setStyleSheet("background-color: #cc0000")
            normalLabel.move(self.pixmap.width() / 2 - 200, 600)
            normalLabel.show()
        elif len(self.currentMoves) < 4:
            currentCity = cities[players[self.currentPlayer].city]
            self.rowOneButtonIndex = 0
            for index, move in enumerate(players[self.currentPlayer].getMoves()):
                self.makeMoveButton(partial(self.movePlayer, players[self.currentPlayer], move), cities[move].name, (115 * index+1) + 10, self.pixmap.height()+ 25, color=cities[move].getColor())
                self.rowOneButtonIndex = self.rowOneButtonIndex + 1

            self.drawRSMoves()

            rowTwoButtonIndex = 0
            for colorIndex in range(0, 4):
                if currentCity.cubeColors[colorIndex] > 0:
                    color = currentCity.indexToColor(colorIndex)
                    self.makeMoveButton(partial(self.removeCube, players[self.currentPlayer].city, color),
                                        "Treat " + color, (115 * rowTwoButtonIndex + 1) + 10, self.pixmap.height() + 80)
                    rowTwoButtonIndex = rowTwoButtonIndex + 1

            if players[self.currentPlayer].color == "LightGreen" and not currentCity.rs:
                self.makeMoveButton(partial(self.placeResearchStation, players[self.currentPlayer].city),
                                    "Make Research Station", (115 * rowTwoButtonIndex + 1) + 10,
                                    self.pixmap.height() + 80, fontSize=10)
                rowTwoButtonIndex = rowTwoButtonIndex + 1

            colorCount = [0, 0, 0, 0]
            for card in players[self.currentPlayer].hand.items():
                if card[0] == players[self.currentPlayer].city and not cities[card[0]].rs and not players[self.currentPlayer].color == "LightGreen":
                    self.makeMoveButton(partial(self.placeResearchStation, card[0], discard=True),
                                        "Make Research Station", (115 * rowTwoButtonIndex + 1) + 10,
                                        self.pixmap.height() + 80, fontSize=10)
                    rowTwoButtonIndex = rowTwoButtonIndex + 1
                elif currentCity.rs:
                    colorIndex = currentCity.colorToIndex(card[1].color)
                    colorCount[colorIndex] = colorCount[colorIndex] + 1

            for index, count in enumerate(colorCount):
                if players[self.currentPlayer].color == "White" and count >= 4:
                    color = currentCity.indexToColor(index)
                    if not self.cures[index]:
                        self.makeMoveButton(partial(self.cure, color, players[self.currentPlayer], True),
                                            "Cure " + color, (115 * rowTwoButtonIndex + 1) + 10,
                                            self.pixmap.height() + 80)
                        rowTwoButtonIndex = rowTwoButtonIndex + 1
                elif count >= 5:
                    color = currentCity.indexToColor(index)
                    if not self.cures[index]:
                        self.makeMoveButton(partial(self.cure, color, players[self.currentPlayer], False),
                                            "Cure " + color, (115 * rowTwoButtonIndex + 1) + 10,
                                            self.pixmap.height() + 80)
                        rowTwoButtonIndex = rowTwoButtonIndex + 1

            rowThreeButtonIndex = 0
            yIndex = 0
            if not players[self.currentPlayer].color == "Brown":
                if players[self.currentPlayer].city in players[self.currentPlayer].hand.keys():
                    for playerIndex, player in enumerate(players):
                        if not player == players[self.currentPlayer] and players[self.currentPlayer].city == player.city:
                            self.makeMoveButton(partial(self.shareKnowledge, players[self.currentPlayer], player, player.city),
                                                "Give P" + str(playerIndex + 1) + " " + currentCity.name,
                                                (115 * rowThreeButtonIndex + 1) + 10,
                                                self.pixmap.height() + 140, fontSize=9)
                            rowThreeButtonIndex = rowThreeButtonIndex + 1
            else:
                for initials, card in players[self.currentPlayer].hand.items():
                    for playerIndex, player in enumerate(players):
                        if not player == players[self.currentPlayer] and players[self.currentPlayer].city == player.city:
                            self.makeMoveButton(
                                partial(self.shareKnowledge, players[self.currentPlayer], player, card.initials),
                                "Give P" + str(playerIndex + 1) + " " + card.name,
                                (115 * rowThreeButtonIndex + 1) + 10,
                                self.pixmap.height() + 140 + (35 * yIndex), fontSize=9)
                            rowThreeButtonIndex = rowThreeButtonIndex + 1
                            if rowThreeButtonIndex == 13:
                                rowThreeButtonIndex = 0
                                yIndex = yIndex + 1

            for playerIndex, player in enumerate(players):
                if players[self.currentPlayer].city in player.hand.keys():
                    if not player == players[self.currentPlayer] and players[self.currentPlayer].city == player.city:
                        self.makeMoveButton(partial(self.shareKnowledge, player, players[self.currentPlayer], player.city),
                                            "Take P" + str(playerIndex + 1) + " " + currentCity.name,
                                            (115 * rowThreeButtonIndex + 1) + 10,
                                            self.pixmap.height() + 140, fontSize=9)
                        rowThreeButtonIndex = rowThreeButtonIndex + 1
                if player.color == "Brown" and not player == players[self.currentPlayer]:
                    for initials, card in player.hand.items():
                        if players[self.currentPlayer].city == player.city:
                            self.makeMoveButton(
                                partial(self.shareKnowledge, player, players[self.currentPlayer], card.initials),
                                "Take P" + str(playerIndex + 1) + " " + card.name,
                                (115 * rowThreeButtonIndex + 1) + 10,
                                self.pixmap.height() + 140 + (35 * yIndex), fontSize=9)
                            rowThreeButtonIndex = rowThreeButtonIndex + 1
                            if rowThreeButtonIndex == 13:
                                rowThreeButtonIndex = 0
                                yIndex = yIndex + 1
            self.rowOneButtonIndex = 0


        else:
            self.makeMoveButton(self.endTurn, "End Turn?", 10, self.pixmap.height() + 25)

    def drawRSMoves(self):
        currentCity = cities[players[self.currentPlayer].city]
        discard = False
        if self.goToRS:
            discard = True
        for rs in self.rsLocations:
            if (self.goToRS or currentCity.rs) and players[self.currentPlayer].city != rs:
                self.makeMoveButton(partial(self.movePlayer, players[self.currentPlayer], rs, discard=discard),
                                    cities[rs].name + " RS", (115 * self.rowOneButtonIndex + 1) + 10,
                                    self.pixmap.height() + 25)
                self.rowOneButtonIndex = self.rowOneButtonIndex + 1
        if self.rsCard:
            self.makeMoveButton(partial(self.movePlayer, players[self.currentPlayer], self.rsCard.initials, discard=discard),
                                self.rsCard.name, (115 * self.rowOneButtonIndex + 1) + 10,
                                self.pixmap.height() + 25)
            self.rowOneButtonIndex = self.rowOneButtonIndex + 1
            self.rsCard = None

    def drawInfectionCards(self):
        for cardInitials, card in infectDeck.discard.items():
            self.makeMoveButton(partial(self.removeInfectCard, card),
                                 card.name, (115 * self.rowOneButtonIndex + 1) + 10,
                                self.pixmap.height() + 25)
            self.rowOneButtonIndex = self.rowOneButtonIndex + 1

    def removeInfectCard(self, card):
        infectDeck.removeFromDiscard(card)
        self.cityResist = False
        self.updateMap()

    def removePlayerCard(self, player, card):
        player.removeCard(card.initials)
        if len(player.hand.items()) <= 7:
            player.handFull = False
        self.updateMap()
        self.canUndo = True

    def balanceHand(self, player):
        self.rowOneButtonIndex = 0
        for name, card in player.hand.items():
            self.makeMoveButton(partial(self.removePlayerCard, player, card),
                                card.name, (115 * self.rowOneButtonIndex + 1) + 10,
                                self.pixmap.height() + 25, color=card.getBackgroundColor())
            self.rowOneButtonIndex = self.rowOneButtonIndex + 1
        self.moveLabel.setText("Player " + str(player.number + 1) +
                               ": Your hand is full, discard till you have 7 cards")
        self.moveLabel.adjustSize()
        self.moveLabel.show()
        self.canUndo = False

    # Delete objects, check board state, redraw board
    def updateMap(self):
        orangeIndex = Setup.getPlayerIndex("Orange")
        if orangeIndex >= 0:
                self.removeAll(players[orangeIndex].city, move=False, update=False)

        for cureIndex, cure in enumerate(self.cures):
            if cure and self.cubeCount[cureIndex] == 0:
                self.eradicated[cureIndex] = True

        for cube in self.cubes:
            cube.deleteLater()
        self.cubes = []
        for r in self.rs:
            r.deleteLater()
        self.rs = []
        for playerLabel in self.playerLabels:
            playerLabel.deleteLater()
        self.playerLabels = []
        for button in self.moveButtons:
            button.deleteLater()
        self.moveButtons = []
        for cardButton in self.handButtons:
            cardButton.deleteLater()
        self.handButtons = []
        for textBox in self.textBoxes:
            textBox.deleteLater()
        self.textBoxes = []
        for cureLabel in self.cureLabels:
            cureLabel.deleteLater()
        self.cureLabels = []

        self.drawMap()
        self.drawPlayers()

        for player in players:
            if player.handFull and not self.loser:
                self.balanceHand(player)
                return

        if self.currentlyMoving:
            for cityInitials, cityToMoveTo in cities.items():
                player = players[self.currentPlayer]
                if not player.city == cityInitials:
                    font = self.cityLabels[cityInitials].font()
                    fm = QFontMetrics(font)
                    width = fm.width(self.cityLabels[cityInitials].text()) + 10
                    height = fm.height()
                    self.makeMoveButton(partial(self.movePlayer, player, cityInitials, discard=True),
                                        cityToMoveTo.name, cityToMoveTo.posX - 9, cityToMoveTo.posY - 9,
                                        color=cityToMoveTo.getColor(), width=width, height=height + 10)
            self.makeMoveButton(None, "Select a City", 10, self.pixmap.height() + 25)
        elif self.researchGrant:
            for cityInitials, cityToRS in cities.items():
                if cityInitials not in self.rsLocations:
                    font = self.cityLabels[cityInitials].font()
                    fm = QFontMetrics(font)
                    width = fm.width(self.cityLabels[cityInitials].text()) + 10
                    height = fm.height()
                    self.makeMoveButton(partial(self.placeResearchStation, cityInitials, discard=False),
                                        cityToRS.name, cityToRS.posX - 9, cityToRS.posY - 9,
                                        color=cityToRS.getColor(), width=width, height=height + 10)
            self.makeMoveButton(None, "Select a City", 10, self.pixmap.height() + 25)
        elif self.goToRS:
            self.drawRSMoves()
        elif self.cityResist:
            self.drawInfectionCards()
        else:
            self.drawMoves()
        self.showFullScreen()

    def movePlayer(self, player, move, discard=False):
        color = cities[move].color
        colorIndex = self.colorToIndex(color)
        if not discard:
            if player.color == "Orange" and self.cures[colorIndex]:
                self.removeAll(move)
            else:
                self.currentMoves.append(Action("move", city=player.city))
        player.moveTo(move)
        self.canUndo = True
        self.currentlyMoving = False
        self.goToRS = False
        self.updateMap()

    def discard(self, player, card):
        if card.color == "gold":
            self.eventCard(player, card)
        elif player == players[self.currentPlayer] and len(self.currentMoves) < 4:
            if player.color == "Orange":
                self.removeAll(card.initials, move=True, cards=card)
            else:
                self.currentMoves.append(Action("discard", city=player.city, cards=card))
            if player.city == card.initials:
                self.currentlyMoving = True
                self.canUndo = False
                player.removeCard(card.initials)
                self.updateMap()
            elif player.color == "LightGreen" and not cities[player.city].rs:
                self.goToRS = True
                self.canUndo = False
                player.removeCard(card.initials)
                self.rsCard = card
                self.updateMap()
            elif not self.currentlyMoving:
                player.removeCard(card.initials)
                self.movePlayer(player, card.initials, discard=True)
                self.updateMap()

    def cure(self, color, player, playerScientist):
        cardsToRemove = 5
        if playerScientist:
            cardsToRemove = 4
        cards = list(player.hand.values())
        discard = []
        handIndex = 0
        while True:
            if cards[handIndex].color == color:
                discard.append(cards[handIndex])
                player.removeCard(cards[handIndex].initials)
                cardsToRemove = cardsToRemove - 1
            if cardsToRemove == 0:
                break
            handIndex = handIndex + 1

        self.currentMoves.append(Action("cure", color=color, cards=discard))

        orange = False
        city = ""
        for player in players:
            if player.color == "Orange":
                orange = True
                city = player.city
        if orange:
            self.removeAll(city, move=False)

        cureIndex = self.colorToIndex(color)
        self.cures[cureIndex] = True

        if all(cure for cure in self.cures):
            self.win()
        self.updateMap()

    def shareKnowledge(self, player1, player2, city):
        card = player1.removeCard(city)[1]
        player2.addCard(card)
        self.currentMoves.append(Action("share", player1=player1, player2=player2, cards=card))
        self.updateMap()

    def placeResearchStation(self, city, discard=True):
        if discard:
            self.currentMoves.append(Action("rs", city=city, cards=players[self.currentPlayer].getCard(city)))
            players[self.currentPlayer].removeCard(city)
        if not self.researchGrant:
            self.currentMoves.append(Action("rs", city=city, cards=None))
        self.canUndo = True
        self.researchGrant = False
        self.rsLocations.append(city)
        cities[city].rs = True
        self.updateMap()

    def removeCube(self, city, color):
        currentCity = cities[city]
        numberOfCubes = 1
        colorIndex = currentCity.colorToIndex(color)
        if players[self.currentPlayer].color == "Orange" or self.cures[colorIndex]:
            numberOfCubes = currentCity.cubeColors[colorIndex]
        self.currentMoves.append(Action("treat", color=color, city=city, number=numberOfCubes))
        currentCity.treat(color, numberOfCubes)
        self.updateMap()

    def removeAll(self, city, move=True, update=True, cards=None):
        currentCity = cities[city]
        if move:
            self.currentMoves.append(Action("medic", color=currentCity.cubeColors, city=players[self.currentPlayer].city, cards=cards))
        for cureIndex, cure in enumerate(self.cures):
            if cure:
                currentCity.treat(self.indexToColor(cureIndex), currentCity.cubeColors[cureIndex])
        if update:
            self.updateMap()

    def eventCard(self, player, card):
        print(card.name)
        if card.name == "Quiet Night":
            self.quietNight = True
        elif card.name == "Airlift":
            self.currentlyMoving = True
            self.canUndo = False
        elif card.name == "City Resist":
            self.cityResist = True
        elif card.name == "Travel Ban":
            self.travelBan = (True, 3)
        elif card.name == "Research Grant":
            self.researchGrant = True
            self.canUndo = False
        else:
            return
        player.removeCard(card.initials)
        self.updateMap()

    def endTurn(self):
        if self.currentlyMoving or self.researchGrant:
            return

        eradicatedList = []
        for colorIndex, eradicatedColor in enumerate(self.eradicated):
            if eradicatedColor:
                eradicatedList.append(self.indexToColor(colorIndex))

        blackList = []
        darkGreenIndex = Setup.getPlayerIndex("DarkGreen")
        if darkGreenIndex >= 0:
            blackList.append(cities[players[darkGreenIndex].city].name)
            for blackListCity in cities[players[darkGreenIndex].city].neighbors:
                blackList.append(cities[blackListCity].name)

        self.currentMoves = []

        #Draw player cards
        epidemic = False
        for x in range(0, 2):
            if playerDeck.deck:
                tempPlayerCard = playerDeck.deck.popitem(last=False)
                if "Epidemic" not in tempPlayerCard[1].name:
                    players[self.currentPlayer].addCard(tempPlayerCard[1])
                else:
                    playerDeck.addToDiscard(tempPlayerCard[1])
                    epidemic = True
            else:
                self.lose("Player Deck Empty")
                break

        #Change Player
        if self.currentPlayer == 3:
            self.currentPlayer = 0
        else:
            self.currentPlayer = self.currentPlayer + 1

        if epidemic:
            self.currentInfectionRate = self.currentInfectionRate + 1
            cityInitials = infectDeck.draw(bottom=True)
            color = cities[cityInitials].color
            cities[cityInitials].infect(color, 3, blackList, eradicatedList)
            infectDeck.intensify()

        #Infect
        if infectDeck and not self.quietNight:
            infectRate = self.infectionRates[self.currentInfectionRate]
            if self.travelBan[0]:
                infectRate = 1
            for infectStep in range(0, infectRate):
                cityInitials = infectDeck.draw()
                color = cities[cityInitials].color
                outbreak = False
                if not self.eradicated[self.colorToIndex(color)]:
                    outbreak = cities[cityInitials].infect(color, 1, blackList, eradicatedList)
                if outbreak:
                    for cityInitials in cities:
                        cities[cityInitials].calm = True
                for cityInitials in cities:
                    cities[cityInitials].calm = True
        else:
            self.quietNight = False

        if self.travelBan[1] == 0:
            self.travelBan = (False, -1)
        elif self.travelBan[0]:
            self.travelBan = (True, self.travelBan[1] - 1)

        #Update outbreak counter
        self.outbreakCounter = 0
        for cityInitials in cities:
            self.outbreakCounter = self.outbreakCounter + cities[cityInitials].outbreakCount
            if self.outbreakCounter >= 8:
                self.lose(str(self.outbreakCounter) + " outbreaks occurred")
                break
        self.updateMap()

        #Count cubes of each color on the board
        for colorIndex, colorCount in enumerate(self.cubeCount):
            if colorCount > 24:
                self.lose(str(colorCount) + " " + self.indexToColor(colorIndex) + " cubes on the board." )
                break

        self.updateMap()

    #Context sensitive undo last move
    def undo(self):
        if len(self.currentMoves) > 0 and self.canUndo:
            lastMove = self.currentMoves.pop(len(self.currentMoves)-1)
            print(str(len(self.currentMoves)) + ": " + lastMove.action)
            if lastMove.action == "cure":
                for card in lastMove.cards:
                    players[self.currentPlayer].addCard(card)
                self.cures[self.colorToIndex(lastMove.color)] = False
            elif lastMove.action == "rs":
                cities[lastMove.city].rs = False
                self.rsLocations.remove(lastMove.city)
                if lastMove.cards:
                    players[self.currentPlayer].addCard(lastMove.cards)
            elif lastMove.action == "move":
                players[self.currentPlayer].city = lastMove.city
            elif lastMove.action == "discard":
                players[self.currentPlayer].city = lastMove.city
                players[self.currentPlayer].addCard(lastMove.cards)
            elif lastMove.action == "treat":
                cities[lastMove.city].infect(lastMove.color, lastMove.number)
            elif lastMove.action == "share":
                if not playerDeck.discard[lastMove.cards.initials]:
                    lastMove.player2.removeCard(lastMove.cards.initials)
                lastMove.player1.addCard(lastMove.cards)
            elif lastMove.action == "medic":
                currentCity = cities[players[self.currentPlayer].city]
                for colorIndex in range(0, 4):
                    currentCity.infect(self.indexToColor(colorIndex), lastMove.color[colorIndex])
                players[self.currentPlayer].city = lastMove.city
                if lastMove.cards:
                    players[self.currentPlayer].addCard(lastMove.cards)
            self.updateMap()
            print("\n")
        pass

    def restart(self):
        self.close()
        subprocess.call("python3 " + "MainWindow.py")

    def win(self):
        cities["Ny"].name = "Gotham City"
        cities["Wa"].name = " Metropolis  "
        self.winner = True
        pass

    def lose(self, cause):
        if Setup.cheatingMode:
            return
        cities["Ny"].name = "Gotham City"
        self.updateMap()
        print("lose: " + cause)
        self.loser = True
        signalLabel = QLabel(self)
        signalLabel.setPixmap(QPixmap('imgs/signal.png'))
        signalLabel.move(self.cityLabels["Ny"].x() - 17, self.cityLabels["Ny"].y() + 5)
        signalLabel.setScaledContents(True)
        signalLabel.resize(15, 10)
        signalLabel.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap.width(), self.pixmap.height(), self.pixmap)
        pen = QPen(Qt.yellow, 3)
        painter.setPen(pen)
        for cityInitials in cities:
            for neighbor in cities[cityInitials].neighbors:
                if cityInitials == "Sf" and neighbor == "To":
                    painter.drawLine(cities[cityInitials].posX + 15, cities[cityInitials].posY + 7,
                                     0, cities[neighbor].posY + 7)
                elif cityInitials == "Sf" and neighbor == "Man" or cityInitials == "La" and neighbor == "Sy":
                    painter.drawLine(cities[cityInitials].posX + 15, cities[cityInitials].posY + 7,
                                     0, (cities[neighbor].posY + 7) / 2 + 25)
                elif cityInitials == "To" and neighbor == "Sf":
                    painter.drawLine(cities[cityInitials].posX + 15, cities[cityInitials].posY + 7,
                                     self.pixmap.width(), cities[neighbor].posY + 7)
                elif cityInitials == "Man" and neighbor == "Sf" or cityInitials == "Sy" and neighbor == "La":
                    painter.drawLine(cities[cityInitials].posX + 15, cities[cityInitials].posY + 7,
                                     self.pixmap.width(), (cities[neighbor].posY + 7) * 2)
                else:
                    painter.drawLine(cities[cityInitials].posX + 15, cities[cityInitials].posY + 7,
                                     cities[neighbor].posX + 15, cities[neighbor].posY + 7)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())