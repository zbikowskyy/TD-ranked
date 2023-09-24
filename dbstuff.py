import sqlite3 as sql

connection = sql.connect ('Touchdownplayers.db')

cursor = connection.cursor()

def tablegracze():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gracze (
        nazwa TEXT,
        zagrane INTEGER,
        wygrane INTEGER,
        elo INTEGER
    )
    """)

def cleargracze():
    cursor.execute("""
    DELETE FROM gracze
    """)

def tablegraczesee():
    cursor.execute("""
    SELECT * FROM gracze
    """)

    for sublist in cursor.fetchall():
        for i, item in enumerate(sublist):
            print(str(item).ljust(20), end='')
        print()

TDRM = {
    1: tablegracze(),
    2: cleargracze(),
    3: tablegraczesee()
}

if __name__ == "__main__":
    print("========== TDR management console ==========\n"
          "1: Zregenerowanie tabeli statystyk graczy\n"
          "2: Usuniecie wszystkiego z tabeli graczy\n"
          "3: Pokazanie statystyk wszystkich graczy\n")
    kmd = input("Komenda: ")

    try:
        TDRM[int(kmd)]
    except:
        print("Zla komenda")

connection.commit()
connection.close()