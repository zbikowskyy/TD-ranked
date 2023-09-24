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

tablegraczesee()

connection.commit()
connection.close()
