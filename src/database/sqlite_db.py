import sqlite3 

DATABASE_PATH = "vai_na_boa.db"

def get_connetcion():
    return sqlite3.connect(DATABASE_PATH)

