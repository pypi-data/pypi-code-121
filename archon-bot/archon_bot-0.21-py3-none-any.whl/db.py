import asyncio
import contextlib
import os
import logging
import pkg_resources
import psycopg2
import psycopg2.extensions
import psycopg2.extras

logger = logging.getLogger()
version = pkg_resources.Environment()["archon-bot"][0].version
DB_USER = os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PWD")
psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
psycopg2.extensions.register_adapter(list, psycopg2.extras.Json)
CONNECTION = asyncio.Queue(maxsize=10)


@contextlib.asynccontextmanager
async def connection():
    conn = await CONNECTION.get_nowait()
    try:
        yield conn
    except:  # noqa: E722
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        CONNECTION.put_nowait(conn)


async def init():
    while True:
        try:
            conn = CONNECTION.get_nowait()
            conn.close()
        except asyncio.QueueEmpty:
            break
    for _ in range(CONNECTION.maxsize):
        CONNECTION.put_nowait(
            psycopg2.connect(
                dbname="archon",
                user=DB_USER,
                password=DB_PWD,
            )
        )
    async with connection() as conn:
        cursor = conn.cursor()
        logger.debug("Initialising DB")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tournament("
            "active INTEGER, "
            "prefix TEXT, "
            "guild TEXT, "
            "category TEXT, "
            "data json)"
        )


def create_tournament(conn, prefix, guild_id, category_id, tournament_data):
    cursor = conn.cursor()
    logger.debug("New tournament %s-%s: %s", guild_id, category_id, tournament_data)
    cursor.execute(
        "INSERT INTO tournament (active, prefix, guild, category, data) "
        "VALUES (1, %s, %s, %s, %s)",
        [
            prefix,
            str(guild_id),
            str(category_id) if category_id else "",
            tournament_data,
        ],
    )


def get_active_prefixes(conn, guild_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT prefix FROM tournament WHERE active=1 AND guild=%s FOR SHARE",
        [str(guild_id)],
    )
    return set(r[0] for r in cursor)


async def get_active_tournaments(conn, guild_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT data from tournament WHERE active=1 AND guild=%s FOR SHARE",
        [str(guild_id)],
    )
    return list(r[0] for r in cursor)


def update_tournament(conn, guild_id, category_id, tournament_data):
    cursor = conn.cursor()
    logger.debug("Update tournament %s-%s: %s", guild_id, category_id, tournament_data)
    cursor.execute(
        "UPDATE tournament SET data=%s WHERE active=1 AND guild=%s AND category=%s",
        [
            tournament_data,
            str(guild_id),
            str(category_id) if category_id else "",
        ],
    )


@contextlib.asynccontextmanager
async def tournament(guild_id, category_id, update=False):
    """Context manager to access a tournament object.

    Handles DB transactions (commit, rollback) and asyncio lock for write operations
    """
    async with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT data from tournament WHERE active=1 AND guild=%s AND category=%s"
            + (" FOR UPDATE" if update else ""),
            [str(guild_id), str(category_id) if category_id else ""],
        )
        tournament = cursor.fetchone()
        if tournament:
            yield conn, tournament[0]
        else:
            yield conn, None


def close_tournament(conn, guild_id, category_id):
    cursor = conn.cursor()
    logger.debug("Closing tournament %s-%s", guild_id, category_id)
    cursor.execute(
        "UPDATE tournament SET active=0 WHERE active=1 AND guild=%s AND category=%s",
        [str(guild_id), str(category_id) if category_id else ""],
    )
