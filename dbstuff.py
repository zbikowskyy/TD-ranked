import sqlite3 as sql

def tablegracze():
    connection = sql.connect('Touchdownplayers.db')
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gracze (
        nazwa TEXT,
        zagrane INTEGER,
        wygrane INTEGER,
        elo INTEGER
    )
    """)

    connection.commit()
    connection.close()

def cleargracze():
    connection = sql.connect('Touchdownplayers.db')
    cursor = connection.cursor()

    cursor.execute("""
    DELETE FROM gracze
    """)

    connection.commit()
    connection.close()

def tablegraczesee():
    connection = sql.connect('Touchdownplayers.db')
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM gracze
    """)

    for sublist in cursor.fetchall():
        for _, item in enumerate(sublist):
            print(str(item).ljust(20), end='')
        print()

    connection.commit()
    connection.close()

if __name__ == "__main__":
    print("========== TDR management console ==========\n"
          "1: Zregenerowanie tabeli statystyk graczy\n"
          "2: Usuniecie wszystkiego z tabeli graczy\n"
          "3: Pokazanie statystyk wszystkich graczy\n")

    try:
        kmd = int(input("Komenda: "))
    except ValueError:
        kmd = 99

    if kmd == 1:
        tablegracze()
    elif kmd == 2:
        cleargracze()
    elif kmd == 3:
        tablegraczesee()
    else:
        print("Zla komenda")
