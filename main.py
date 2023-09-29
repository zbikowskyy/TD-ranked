import sqlite3 as sql
import pickle
#[nazwa, zagrane, wygrane, elo]

graczid = { #tlumacz id na nazwy bo latwiej
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

copy = lambda obj: pickle.loads(pickle.dumps(obj)) #kopia klasy funkcja

class Player:#klasa gracz
    def __init__(self, name=""): #przy nowej instancji
        self.name = name
        self.wygrane = 0
        self.zagrane = 0
        self.elo = 100
        self.przegrane = self.zagrane - self.wygrane
        try:
            self.winrate = self.wygrane / self.przegrane
        except:
            self.winrate = 0

    def __str__(self):#przy print() zeby statystyki
        return f"Nazwa: {self.name : <20}, Zagrane gry: {self.zagrane : <5}, Wygrane gry: {self.wygrane : <5}, Winrate: {str(self.winrate)[:4] : <5}, Elo: {str(self.elo)[:6] : <20}".ljust(25)

    def insert_player(self): #dodaje gracza do db
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor() #lacze z db

        cursor.execute("""
        INSERT INTO gracze VALUES
        ('{}', 0, 0, 100)
        """.format(self.name)) #daje defaultowe staty

        connection.commit()
        connection.close()#zamkniecie lacza

    def load_player(self, nazwa):#pobiera dane z db
        self.name = nazwa #zmienic zeby bralo id
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()#lacze z db

        cursor.execute("""
        SELECT * FROM gracze
        WHERE nazwa = '{}'
        """.format(nazwa))

        results = cursor.fetchone() #pobranie z db danych

        self.zagrane = results[1]
        self.wygrane = results[2]
        self.elo = results[3]

        try:
            self.winrate = self.wygrane / self.zagrane #winrate
        except:
            self.winrate = 0

        connection.close()

    def addgames(self, zagrane, wygrane): #ustawia staty po grach ###CHYBA DO ZMIANY NOY SHURE
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()#lacze z db

        cursor.executescript("""
        UPDATE gracze SET zagrane = {} WHERE nazwa = '{}';
        UPDATE gracze SET wygrane = {} WHERE nazwa = '{}';
        """.format(self.zagrane + zagrane, self.name, self.wygrane + wygrane, self.name))#update win/lose

        connection.commit()
        connection.close()#koniec lacza

        self.wygrane += wygrane
        self.zagrane += zagrane
        self.przegrane += zagrane - wygrane
        try:
            self.winrate = self.wygrane/self.przegrane
        except:
            self.winrate = 0

    def getnameElo(self):#daje nazwe i elo ###chyba useless
        return f"{self.name: <15} - {self.elo: <5}"

class Game:#klasa gry
    def __init__(self, ids): #ids = lista id graczy [wygrany, wygrany, przegrany, przegrany]
        self.nr = 0
        self.gracze = []

        nazwy = []
        for i in ids: nazwy.append(graczid[i]) #nazwy z id

        for nazwa in nazwy:#twory liste graczy jako klasy
            print(nazwa)
            player = Player()
            player.load_player(nazwa)
            self.gracze.append(player)

        self.wygrani = [self.gracze[0], self.gracze[1]]#dzieli ta liste na dwie nowe
        self.przegrani = [self.gracze[2], self.gracze[3]]

    def __str__(self): #do print()
        return f"Nr gry: {self.nr: < 3}, Wygrani: {self.wygrani[0].getnameElo()}, {self.wygrani[1].getnameElo()}, " \
               f"Przegrani: {self.przegrani[0].getnameElo()}, {self.przegrani[1].getnameElo()}"

    def evaluategame(self): #kalkulacja gry
        elowygranych = self.wygrani[0].elo + self.wygrani[1].elo
        eloprzegranych = self.przegrani[0].elo + self.przegrani[1].elo

        try: dif = eloprzegranych / elowygranych
        except: dif = 0 #roznica

        multipliyer = 0.2 * dif * dif + dif  # y = 0.2x^2 + x
        print(multipliyer)#mnoznik

        self.wygrani[0].elo += 20 * elowygranych     / self.wygrani[0].elo * multipliyer  # druzyna lacznie zyskuje 20*mnoznik a przegrana tyle traci
        self.wygrani[1].elo += 20 * elowygranych     / self.wygrani[1].elo * multipliyer
        self.przegrani[0].elo -= 20 * eloprzegranych / self.przegrani[1].elo * multipliyer  # piekne
        self.przegrani[1].elo -= 20 * eloprzegranych / self.przegrani[0].elo * multipliyer #kalkulacja elo

        if self.przegrani[0].elo < 0: self.przegrani[0].elo = 0
        if self.przegrani[1].elo < 0: self.przegrani[1].elo = 0 #ustawianie elo ig

        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()#lacze z db

        for gracz in [self.wygrani[0], self.wygrani[1], self.przegrani[0], self.przegrani[1]]:
            cursor.execute("UPDATE gracze SET elo = {} WHERE nazwa = '{}'".format(gracz.elo, gracz.name)) #update elo ###chyba sie kluci z Player.addgame()
        #monkey brain start work

        connection.commit()
        connection.close()#koniec db

        for i in self.wygrani: i.addgames(1,1)
        for i in self.przegrani: i.addgames(1,0)

        self.remberstats = []
        for i in self.wygrani + self.przegrani: self.remberstats.append(i.getnameElo())
        print(self.remberstats)#zeby mozna bylo odczytywac bez ewaluacji ale to nie ma sensuuuuuu

def detailedstats(): #staty kazdego gracza
    for i in graczid.keys():
        playr = Player()
        playr.load_player(graczid[i])
        print(playr)

def dziennegry(gry, calc = 0): #kalkualcja gier gdy calc = 1 a tak to staty gier
    if calc == 1:
        for i, game in enumerate(gry): game.nr = i + 1
        for game in gry: game.evaluategame()

    for game in gry: print(game)

def addbackplayers(): #po resecie db to trza
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
    grydzis = [
        Game([3, 4, 5, 1]),
        Game([3, 5, 1, 6]),
        Game([5, 7, 3, 10]),
        Game([3, 8, 5, 6]),
        Game([8, 10, 9, 5]),
        Game([3, 8, 5, 6]),
        Game([3, 8, 6, 5]),
        Game([6, 10, 3, 8]),
        Game([3, 5, 6, 8]),
        Game([5, 8, 3, 6]),
        Game([8, 3, 9, 6]),
        Game([8, 3, 6, 9]),
        Game([3, 6, 8, 1])
    ]

    dziennegry(grydzis, calc=1)
    detailedstats()