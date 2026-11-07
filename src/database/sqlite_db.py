import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = str(BASE_DIR / "vai_na_boa.db")


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# Alias para manter compatibilidade com os repositórios existentes
def get_connetcion():
    return get_connection()
