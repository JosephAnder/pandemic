class Action:
    def __init__(self, action, player1=None, player2=None, color=None, city=None, cards=None, number=None):
        self.player1 = player1
        self.player2 = player2
        self.action = action
        self.color = color
        self.city = city
        self.cards = cards
        self.number = number