from database.migration_runner import executar_migrations


def criar_tabela():
    return executar_migrations()


if __name__ == "__main__":
    criar_tabela()
