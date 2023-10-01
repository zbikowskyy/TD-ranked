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
clamp = lambda n, minn, maxn: max(min(maxn, n), minn) #limit min i max

class Player:#klasa gracz
    def __init__(self, id, load=1): #przy nowej instancji (konstruktor?)
        self.id = id
        self.name = graczid[id]

        if load:
            self.load_player()
        else: self.insert_player()

    def __str__(self):#przy print() zeby statystyki
        return f"Nazwa: {self.name : <20}, " \
               f"Zagrane gry: {self.zagrane : <5}, " \
               f"Wygrane gry: {self.wygrane : <5}, " \
               f"Winrate: {str(self.winrate)[:4] : <5}, " \
               f"Elo: {str(self.elo)[:6] : <20}" #nietykac

    def insert_player(self, zagrane = 0, wygrane = 0, elo = 100): #dodaje gracza do db
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor() #lacze z db

        cursor.execute("""
        INSERT INTO gracze VALUES ('{}', {}, {}, {})
        """.format(graczid[self.id], zagrane, wygrane, elo)) #daje defaultowe staty

        connection.commit()
        connection.close()#zamkniecie lacza
        self.load_player()

    def load_player(self):#pobiera dane z db
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()#lacze z db

        cursor.execute("""
        SELECT * FROM gracze WHERE nazwa = '{}'
        """.format(graczid[self.id]))

        result = cursor.fetchone() #pobranie z db danych

        self.zagrane = result[1]
        self.wygrane = result[2]
        self.elo = result[3]

        try:
            self.winrate = self.wygrane / self.zagrane #winrate
        except:
            self.winrate = 0

        connection.close()

    def wipeplayer(self):
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()

        cursor.execute("""
        DELETE FROM gracze WHERE nazwa = '{}'
        """.format(graczid[self.id]))

        connection.commit()
        connection.close()

    def changeelo(self, newelo): ####jeszcze nie uzyte
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()  # lacze z db

        cursor.execute("""
        UPDATE gracze SET elo = {} WHERE nazwa = '{}'
        """.format(newelo, self.name))

        connection.commit()
        connection.close()  # koniec lacza
        self.elo = newelo

    def changestats(self, newelo, win = True):
        connection = sql.connect("Touchdownplayers.db")
        cursor = connection.cursor()#lacze z db

        self.zagrane += 1
        if win: self.wygrane += 1

        self.wipeplayer()
        self.insert_player(zagrane=self.zagrane, wygrane=self.wygrane, elo=newelo)

        connection.commit()
        connection.close()#koniec lacza

        try:
            self.winrate = self.wygrane/self.przegrane
        except:
            self.winrate = 0


    def getnameElo(self):#daje nazwe i elo ###chyba useless
        return f"{self.name: <15} - {self.elo: <5}" ######TYMCZASOWE WYLACZENIE Z UZYTKU

class Game:#klasa gry
    def __init__(self, ids): #ids = lista id graczy [wygrany, wygrany, przegrany, przegrany]
        self.nr = 0
        self.gracze = []

        for id in ids:#twory liste graczy jako klasy
            player = Player(id)
            self.gracze.append(player)

        self.wygrani = [self.gracze[0], self.gracze[1]]#dzieli ta liste na dwie nowe
        self.przegrani = [self.gracze[2], self.gracze[3]]

    def __str__(self): #do print()
        return f"Nr gry: {self.nr: < 3}, Wygrani: {self.wygrani[0].getnameElo()}, {self.wygrani[1].getnameElo()}, " \
               f"Przegrani: {self.przegrani[0].getnameElo()}, {self.przegrani[1].getnameElo()}"

    def evaluategame(self): #kalkulacja gry
        elolist = [self.wygrani[0].elo, self.wygrani[1].elo, self.przegrani[0].elo, self.przegrani[1].elo]
        elowygranych = elolist[0] + elolist[1]
        eloprzegranych = elolist[2] + elolist[3]

        if elowygranych == 0:
            if eloprzegranych == 0: dif = 1
            else: dif = 2
        else:
            dif = clamp(eloprzegranych / elowygranych, 0, 2)

        multiplier = 0.2 * dif * dif + dif  # y = 0.2x^2 + x
        print(multiplier)#mnoznik

        elolist[0] += 20 * elowygranych   / elolist[0] * multiplier  # druzyna lacznie zyskuje 20*mnoznik a przegrana tyle traci
        elolist[1] += 20 * elowygranych   / elolist[1] * multiplier
        elolist[2] -= 20 * eloprzegranych / elolist[3] * multiplier  # piekne
        elolist[3] -= 20 * eloprzegranych / elolist[2] * multiplier #kalkulacja elo

        print(elolist)

        self.wygrani[0].changestats(newelo=elolist[0])
        self.wygrani[1].changestats(newelo=elolist[1])
        self.przegrani[0].changestats(newelo=elolist[2], win=False)
        self.przegrani[1].changestats(newelo=elolist[3], win=False)
        #monkey brain -start- STOPPED work D:


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
    for i in graczid.keys():
        print(f"Dodaje gracza id {i}")
        x = Player(i, load = 0)


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

