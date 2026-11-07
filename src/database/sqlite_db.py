"""
src/database/sqlite_db.py
Conexao hibrida:
- Usa Turso (LibSQL na nuvem) se TURSO_DATABASE_URL estiver configurada no .env
- Usa SQLite local se nao houver configuracao do Turso
"""
import os
import sys
import sqlite3
from pathlib import Path
import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = str(BASE_DIR / "vai_na_boa.db")

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")


class TursoCursor:
    """Cursor compativel com o padrao DB-API do Python em cima da API HTTP do Turso."""
    def __init__(self, connection):
        self.conn = connection
        self.description = None
        self.rowcount = -1
        self.lastrowid = None
        self._rows = []

    def execute(self, sql, params=()):
        sql_formatado = sql
        args_payload = []

        if params:
            for p in params:
                if p is None:
                    args_payload.append({"type": "null"})
                elif isinstance(p, int):
                    args_payload.append({"type": "integer", "value": str(p)})
                elif isinstance(p, float):
                    args_payload.append({"type": "float", "value": p})
                else:
                    args_payload.append({"type": "text", "value": str(p)})

        pipeline_url = f"{self.conn.http_url}/v2/pipeline"
        headers = {
            "Authorization": f"Bearer {self.conn.auth_token}",
            "Content-Type": "application/json",
        }
        stmt = {"sql": sql_formatado}
        if args_payload:
            stmt["args"] = args_payload

        payload = {
            "requests": [
                {"type": "execute", "stmt": stmt},
                {"type": "close"}
            ]
        }

        resp = requests.post(pipeline_url, json=payload, headers=headers, timeout=12)
        resp.raise_for_status()
        data = resp.json()

        first_res = data.get("results", [])[0]
        if first_res.get("type") == "error":
            raise RuntimeError(f"Erro Turso: {first_res.get('error')}")

        result_obj = first_res.get("response", {}).get("result", {})
        self.lastrowid = result_obj.get("last_insert_rowid")
        self.rowcount = result_obj.get("affected_row_count", 0)

        cols = [c.get("name") for c in result_obj.get("cols", [])]
        self.description = [(c, None, None, None, None, None, None) for c in cols] if cols else None

        raw_rows = result_obj.get("rows", [])
        parsed = []
        for r in raw_rows:
            row_vals = []
            for item in r:
                t = item.get("type")
                v = item.get("value")
                if t == "integer":
                    row_vals.append(int(v) if v is not None else None)
                elif t == "float":
                    row_vals.append(float(v) if v is not None else None)
                else:
                    row_vals.append(v)
            parsed.append(tuple(row_vals))

        self._rows = parsed
        return self

    def fetchone(self):
        return self._rows.pop(0) if self._rows else None

    def fetchall(self):
        res = list(self._rows)
        self._rows = []
        return res

    def close(self):
        pass


class TursoConnection:
    """Wrapper de conexao com Turso que imita sqlite3.Connection"""
    def __init__(self, url, token):
        self.auth_token = token
        raw = url.replace("libsql://", "").replace("https://", "").replace("http://", "")
        self.http_url = f"https://{raw}"

    def cursor(self):
        return TursoCursor(self)

    def execute(self, sql, params=()):
        c = self.cursor()
        c.execute(sql, params)
        return c

    def commit(self):
        pass

    def close(self):
        pass


def get_connection():
    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        return TursoConnection(TURSO_DATABASE_URL, TURSO_AUTH_TOKEN)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_connetcion():
    return get_connection()
