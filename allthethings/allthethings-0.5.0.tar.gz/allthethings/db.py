from urllib.parse import quote as urlquote


def make_dsn(protocol: str, *, host: str, port: int, database: str, username: str, password: str) -> str:
    username = urlquote(username, safe="")
    password = urlquote(password, safe="")

    return f"{protocol}://{username}:{password}@{host}:{port}/{database}"


def make_postgres_dsn(*, host: str, database: str, username: str, password: str, port: int = 5432) -> str:
    return make_dsn(
        protocol='postgresql',
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
    )
