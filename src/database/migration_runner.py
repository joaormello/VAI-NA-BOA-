import shutil
from datetime import datetime
from pathlib import Path
from database.sqlite_db import DATABASE_PATH, BASE_DIR, get_connection

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
BACKUP_DIR = BASE_DIR / "data" / "backups"


def _criar_tabela_migrations(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
    """)
    conn.commit()


def _listar_migrations_aplicadas(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
    return {row[0] for row in cursor.fetchall()}


def _fazer_backup_banco():
    db_file = Path(DATABASE_PATH)
    if not db_file.exists():
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = BACKUP_DIR / f"vai_na_boa_backup_{timestamp}.db"
    shutil.copy2(db_file, destino)
    return destino


def executar_migrations():
    conn = get_connection()
    _criar_tabela_migrations(conn)
    aplicadas = _listar_migrations_aplicadas(conn)

    arquivos_sql = sorted(MIGRATIONS_DIR.glob("*.sql"))
    pendentes = [arq for arq in arquivos_sql if arq.stem not in aplicadas]

    if not pendentes:
        conn.close()
        return []

    backup_path = _fazer_backup_banco()
    if backup_path:
        print(f"💾 Backup automático criado em: {backup_path}")

    executadas = []
    try:
        for arquivo in pendentes:
            versao = arquivo.stem
            sql_script = arquivo.read_text(encoding="utf-8")

            print(f"🔄 Aplicando migration: {versao}...")
            conn.execute("PRAGMA foreign_keys = OFF;")
            conn.executescript(sql_script)

            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (versao, agora),
            )
            conn.commit()
            conn.execute("PRAGMA foreign_keys = ON;")

            fk_errors = conn.execute("PRAGMA foreign_key_check;").fetchall()
            if fk_errors:
                raise RuntimeError(
                    f"Erro de integridade de chave estrangeira em {versao}: {fk_errors}"
                )

            print(f"✅ Migration aplicada com sucesso: {versao}")
            executadas.append(versao)
    finally:
        conn.close()

    return executadas


if __name__ == "__main__":
    aplicadas = executar_migrations()
    if not aplicadas:
        print("✅ Banco de dados já está na versão mais recente (nenhuma migration pendente).")
