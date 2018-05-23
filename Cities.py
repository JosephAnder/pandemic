class City:
    def __init__(self, name, color, neighbors, posX=0, posY=0):
        self.name = name
        self.color = color
        self.neighbors = neighbors
        self.rs = False
        self.players = []
        self.cubeCount = 0
        self.cubeColors = [0, 0, 0, 0]
        self.pop = 0
        self.posX = posX
        self.posY = posY
        self.calm = True
        self.outbreakCount = 0

    def addRS(self):
        self.rs = True

    def getColor(self):
        if self.color == "blue":
            return "#0099ff"
        elif self.color == "yellow":
            return "#ffcc00"
        elif self.color == "red":
            return "#ff5050"
        elif self.color == "black":
            return "#8585ad"

    def getCubes(self):
        colors = []
        tempCubes = [0, 0, 0, 0]
        for x in range(0, 4):
            tempCubes[x] = self.cubeColors[x]
        for x in range(0, 3):
            if tempCubes[0] >= 1:
                colors.append("blue")
                tempCubes[0] = tempCubes[0] - 1
            elif tempCubes[1] >= 1:
                colors.append("yellow")
                tempCubes[1] = tempCubes[1] - 1
            elif tempCubes[2] >= 1:
                colors.append("black")
                tempCubes[2] = tempCubes[2] - 1
            elif tempCubes[3] >= 1:
                colors.append("red")
                tempCubes[3] = tempCubes[3] - 1
        return colors

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

    def treat(self, color, number=1):
        self.cubeCount = self.cubeCount - number
        index = self.colorToIndex(color)
        self.cubeColors[index] = self.cubeColors[index] - number

    def infect(self, color, number, blackList=[], eradicatedList=[]):
        if not self.name in blackList or self.color in eradicatedList:
            if self.cubeCount >= 3:
                return self.outbreak(blackList)
            else:
                self.cubeCount = self.cubeCount + number
            cubeColor = 0
            if color == "yellow":
                cubeColor = 1
            elif color == "black":
                cubeColor = 2
            elif color == "red":
                cubeColor = 3
            self.cubeColors[cubeColor] = self.cubeColors[cubeColor] + number
        else:
            self.calm = False

    def outbreak(self, blacklist=[], eradicatedList=[]):
        self.calm = False
        self.outbreakCount = self.outbreakCount + 1
        for neighbor in self.neighbors:
            if cities[neighbor].calm:
                cities[neighbor].infect(self.color, 1, blacklist, eradicatedList)
        return True

sf = City("San Francisco", "blue", ["Ch", "La", "To", "Man"], 50, 150)
ch = City("Chicago", "blue", ["At", "Mo", "Sf", "La", "Mc"], 175, 125)
at = City("Atlanta", "blue", ["Ch", "Wa", "Mi"], 200, 200)
wa = City("Washington", "blue", ["At", "Mo", "Ny", "Mi"], 350, 200)
mo = City("Montreal", "blue", ["Ch", "Ny", "Wa"], 300, 100)
ny = City("New York", "blue", ["Wa", "Mo", "Ma", "Lo"], 400, 125)
lo = City("London", "blue", ["Ny", "Ma", "Pa", "Es"], 625, 100)
es = City("Essen", "blue", ["Lo", "Pa", "Ml", "St"], 750, 75)
st = City("St. Petersburg", "blue", ["Es", "Ist", "Ms"], 875, 50)
ml = City("Milan", "blue", ["Es", "Pa", "Ist"], 825, 125)
pa = City("Paris", "blue", ["Lo", "Es", "Ml", "Ma", "Al"], 725, 150)
ma = City("Madrid", "blue", ["Ny", "Lo", "Pa", "Al", "Sp"], 625, 200)

la = City("Los Angeles", "yellow", ["Sf", "Ch", "Mc", "Sy"], 50, 225)
mc = City("Mexico City", "yellow", ["Ch", "La", "Mi", "Bo", "Li"], 150, 275)
mi = City("Miami", "yellow", ["At", "Wa", "Mc", "Bo"], 275, 250)
bo = City("Bogota", "yellow", ["Mc", "Mi", "Li", "Bu", "Sp"], 275, 350)
li = City("Lima", "yellow", ["Mc", "Bo", "Sa"], 275, 450)
sa = City("Santiago", "yellow", ["Li"], 275, 550)
bu = City("Buenos Aires", "yellow", ["Bo", "Sp"], 425, 525)
sp = City("Sao Paulo", "yellow", ["Ma", "Bo", "Lg", "Bu"], 500, 425)
lg = City("Lagos", "yellow", ["Sp", "Kh", "Ki"], 700, 325)
kh = City("Khartoum", "yellow", ["Ca", "Lg", "Ki", "Jo"], 850, 325)
ki = City("Kinshasa", "yellow", ["Lg", "Kh", "Jo"], 800, 400)
jo = City("Johannesburg", "yellow", ["Ki", "Kh"], 850, 500)

al = City("Algiers", "black", ["Ma", "Pa", "Ist", "Ca"], 775, 225)
ist = City("Istanbul", "black", ["St", "Ml", "Al", "Ca", "Ba", "Ms"], 875, 175)
ca = City("Cairo", "black", ["Kh", "Ist", "Al", "Ri", "Ba"], 875, 250)
ms = City("Moscow", "black", ["St", "Ist", "Te"], 975, 100)
ri = City("Riyadh", "black", ["Ba", "Ca", "Ka"], 975, 275)
ba = City("Baghdad", "black", ["Ist", "Ca", "Ri", "Ka", "Te"], 975, 200)
te = City("Tehran", "black", ["Ms", "Ba", "Ka", "De"], 1050, 150)
ka = City("Karachi", "black", ["Te", "Ba", "Ri", "Mu", "De"], 1100, 250)
mu = City("Mumbai", "black", ["De", "Ka", "Che"], 1150, 300)
de = City("Delhi", "black", ["Te", "Ka", "Mu", "Che", "Ko"], 1200, 200)
che = City("Chennai", "black", ["De", "Mu", "Ko", "Ja", "Ban",], 1200, 350)
ko = City("Kolkata", "black", ["De", "Che", "Ban", "Hk"], 1250, 250)

be = City("Beijing", "red", ["Se", "Sh"], 1325, 125)
se = City("Seoul", "red", ["Be", "Sh", "To"], 1425, 150)
sh = City("Shanghai", "red", ["Be", "Hk", "Ta", "To", "Se"], 1350, 200)
to = City("Tokyo", "red", ["Se", "Sh", "Os", "Sf"], 1525, 175)
os = City("Osaka", "red", ["To", "Ta"], 1550, 250)
ta = City("Taipei", "red", ["Sh", "Hk", "Man", "Os"], 1450, 250)
hk = City("Hong Kong", "red", ["Ko", "Ban", "Ho", "Man", "Ta", "Sh"], 1350, 275)
ban = City("Bangkok", "red", ["Ko", "Che", "Ja", "Ho", "Hk"], 1300, 350)
ja = City("Jakarta", "red", ["Ban", "Che", "Sy", "Ho"], 1325, 425)
ho = City("Ho Chi Minh City", "red", ["Hk", "Ban", "Ja", "Man"], 1400, 350)
man = City("Manila", "red", ["Ta", "Hk", "Ho", "Sy", "Sf"], 1550, 375)
sy = City("Sydney", "red", ["Man", "Ja", "La"], 1550, 550)



cities = {
        "Sf": sf, "Ch": ch, "At": at, #Blue Cities
        "Wa": wa, "Mo": mo, "Ny": ny,
        "Lo": lo, "Es": es, "St": st,
        "Ml": ml, "Pa": pa, "Ma": ma,

        "La": la, "Mc": mc, "Mi": mi, #Yellow Cities
        "Bo": bo, "Li": li, "Sa": sa,
        "Bu": bu, "Sp": sp, "Lg": lg,
        "Kh": kh, "Ki": ki, "Jo": jo,

        "Al": al, "Ist": ist, "Ca": ca, #Black Cities
        "Ms": ms, "Ri": ri, "Ba": ba,
        "Te": te, "Ka": ka, "Mu": mu,
        "De": de, "Che": che, "Ko": ko,

        "Be": be, "Se": se, "Sh": sh, #Red Cities
        "To": to, "Os": os, "Ta": ta,
        "Hk": hk, "Ban": ban, "Ja": ja,
        "Ho": ho, "Man": man, "Sy": sy
}
