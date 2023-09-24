import sqlite3 as sql
#[nazwa, zagrane, wygrane, elo]

#komentarz dla testu

graczid = {
    1: "remikulek",
    2: "michsza",
    3: "ItsAllGese",
    4: "OrzyszAnin",
    5: "WeCanScrapTheS",
    6: "InfernoDragon",
    7: "apeliator",
    8: "interboypl",
    9: "BurgerConsumer3",
    10: "wojtekcola",
    11: "Wojtek"
}

class Player:
    def __init__(self, name=""):
        self.name = name
        self.wygrane = 0
        self.zagrane = 0
        self.elo = 100
        self.przegrane = self.zagrane - self.wygrane
        try:
            self.winrate = self.wygrane / self.przegrane
        except:
            self.winrate = 0

    def __str__(self):
        return f"Nazwa: {self.name : <20}, Zagrane gry: {self.zagrane : <5}, Wygrane gry: {self.wygrane : <5}, Winrate: {str(self.winrate)[:4] : <5}, Elo: {str(self.elo)[:6] : <20}".ljust(25)

    def insert_player(self):
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO gracze VALUES
        ('{}', 0, 0, 100)
        """.format(self.name))

        connection.commit()
        connection.close()

    def load_player(self, nazwa):
        self.name = nazwa
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()

        cursor.execute("""
        SELECT * FROM gracze
        WHERE nazwa = '{}'
        """.format(nazwa))

        results = cursor.fetchone()

        self.zagrane = results[1]
        self.wygrane = results[2]
        self.elo = results[3]

        try:
            self.winrate = self.wygrane / self.zagrane
        except:
            self.winrate = 0

        connection.close()

    def addgames(self, zagrane, wygrane):
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()

        cursor.executescript("""
        UPDATE gracze SET zagrane = {} WHERE nazwa = '{}';
        UPDATE gracze SET wygrane = {} WHERE nazwa = '{}';
        """.format(self.zagrane + zagrane, self.name, self.wygrane + wygrane, self.name))

        connection.commit()
        connection.close()

        self.wygrane += wygrane
        self.zagrane += zagrane
        self.przegrane += zagrane - wygrane
        try:
            self.winrate = self.wygrane/self.przegrane
        except:
            self.winrate = 0

    def getnameElo(self):
        return f"{self.name: <15} - {self.elo: <5}"

class Game:
    def __init__(self, ids):
        self.nr = 0
        self.gracze = []

        nazwy = []
        for i in ids: nazwy.append(graczid[i])

        for nazwa in nazwy:
            print(nazwa)
            player = Player()
            player.load_player(nazwa)
            self.gracze.append(nazwa)
        self.wygrani = [self.gracze[0], self.gracze[1]]
        self.przegrani = [self.gracze[2], self.gracze[3]]

    def __str__(self):
        return f"Nr gry: {self.nr: < 3}, Wygrani: {self.wygrani[0].getnameElo()}, {self.wygrani[1].getnameElo()}, Przegrani: {self.przegrani[0].getnameElo()}, {self.przegrani[1].getnameElo()}"

    def evaluategame(self):
        elowygranych = self.wygrani[0].elo + self.wygrani[1].elo
        eloprzegranych = self.przegrani[0].elo + self.przegrani[1].elo

        try: dif = eloprzegranych / elowygranych
        except: dif = 0

        multipliyer = 0.2 * dif * dif + dif  # y = 0.2x^2 + x
        print(multipliyer)

        self.wygrani[0].elo += 20 * elowygranych     / self.wygrani[0].elo * multipliyer  # druzyna lacznie zyskuje 20*mnoznik a przegrana tyle traci
        self.wygrani[1].elo += 20 * elowygranych     / self.wygrani[1].elo * multipliyer
        self.przegrani[0].elo -= 20 * eloprzegranych / self.przegrani[1].elo * multipliyer  # piekne
        self.przegrani[1].elo -= 20 * eloprzegranych / self.przegrani[0].elo * multipliyer

        if self.przegrani[0].elo < 0: self.przegrani[0].elo = 0
        if self.przegrani[1].elo < 0: self.przegrani[1].elo = 0

        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()

        for gracz in [self.wygrani[0], self.wygrani[1], self.przegrani[0], self.przegrani[1]]:
            cursor.execute("UPDATE gracze SET elo = {} WHERE nazwa = '{}'".format(gracz.elo, gracz.name))
        #monkey brain start work

        connection.commit()
        connection.close()

        for i in self.wygrani: i.addgames(1,1)
        for i in self.przegrani: i.addgames(1,0)

        self.remberstats = []
        for i in self.wygrani + self.przegrani: self.remberstats.append(i.getnameElo())
        print(self.remberstats)

def elo_gain(os1,os2,os3,os4):     #do zmiany     #OLDASSS
    #os1 i os2 to osoby wygrane

    elowygranych = os1.elo + os2.elo
    eloprzegranych = os3.elo + os4.elo
    dif = eloprzegranych/elowygranych

    multipliyer = 0.2 * dif * dif + dif #y = 0.2x^2 + x

    os1.elo += 20 * elowygranych / os1.elo * multipliyer  #druzyna lacznie zyskuje 20*mnoznik a przegrana tyle traci
    os2.elo += 20 * elowygranych / os2.elo * multipliyer
    os3.elo -= 20 * eloprzegranych / os4.elo * multipliyer  #piekne
    os4.elo -= 20 * eloprzegranych / os3.elo * multipliyer

    if os3.elo < 0: os3.elo = 0
    if os4.elo < 0: os4.elo = 0

    connection = sql.connect("Touchdownplayers.db")
    cursor = connection.cursor()

    cursor.executescript("""
            UPDATE gracze SET elo = {} WHERE nazwa = '{}';         
            UPDATE gracze SET elo = {} WHERE nazwa = '{}';
            UPDATE gracze SET elo = {} WHERE nazwa = '{}';
            UPDATE gracze SET elo = {} WHERE nazwa = '{}';
            """.format(os1.elo, os1.name, os2.elo, os2.name, os3.elo, os3.name, os4.elo, os4.name))#bing bong ching chong

    connection.commit()
    connection.close()

def addgame(osid1, osid2, osid3, osid4):                                #OLDASSS
    p1 = Player()
    p1.load_player(graczid[osid1])
    p1.addgames(1,1)
    p2 = Player()
    p2.load_player(graczid[osid2])
    p2.addgames(1, 1)
    p3 = Player()
    p3.load_player(graczid[osid3])
    p3.addgames(1, 0)
    p4 = Player()
    p4.load_player(graczid[osid4])
    p4.addgames(1, 0)

    elo_gain(p1,p2,p3,p4)


def detailedstats():
    for i in graczid.keys():
        playr = Player()
        playr.load_player(graczid[i])
        print(playr)

def main():     #OLDASSS
    for _ in range(0,11):
        l = []
        for i in range(0,4):
            idgracza = int(input("{} os. id: ".format(i+1)))
            l.append(idgracza)
        addgame(l[0], l[1], l[2], l[3])

def dziennegry(gry, calc = 0):
    if calc == 1:
        for i, game in enumerate(gry): game.nr = i + 1
        for game in gry: game.evaluategame()

    for game in gry: print(game)

def addbackplayers():
    Player("Wojtek").insert_player()
    Player("OrzyszAnin").insert_player()
    Player("remikulek").insert_player()
    Player("michsza").insert_player()
    Player("ItsAllGese").insert_player()
    Player("WeCanScrapTheS").insert_player()
    Player("InfernoDragon").insert_player()
    Player("apeliator").insert_player()
    Player("interboypl").insert_player()
    Player("BurgerConsumer3").insert_player()
    Player("wojtekcola").insert_player()



if __name__ == "__main__":
    #Game([idwygranych, idprzegranych])
    #grydzis = [
    #    Game([3, 4, 5, 1]),
    #    Game([3, 5, 1, 6]),
    #    Game([5, 7, 3, 10]),
    #    Game([3, 8, 5, 6]),
    #    Game([8, 10, 9, 5]),
    #    Game([3, 8, 5, 6]),
    #    Game([3, 8, 6, 5]),
    #    Game([6, 10, 3, 8]),
    #    Game([3, 5, 6, 8]),
    #    Game([5, 8, 3, 6]),
    #    Game([8, 3, 9, 6]),
    #    Game([8, 3, 6, 9]),
    #    Game([3, 6, 8, 1])
    #]

    #dziennegry(Game([3, 4, 5, 1]), calc=1)
    #detailedstats()
    addbackplayers()