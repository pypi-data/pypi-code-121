from datetime import datetime
from sqlalchemy import text
from ..run_statement import RunStatement


def last_sync_id(conn, dst, src):
    last_id = conn.execute(
        text(
            """
            SELECT last_id FROM last_sync
            WHERE dst = :dst AND src = :src
            """
        ),
        dst=dst,
        src=src,
    ).fetchone()

    if last_id is None:
        last_id = 0
    else:
        last_id = last_id[0]

    return last_id


def save_last_sync_id(conn, destination, source, last_id):
    runner = RunStatement()
    flv = runner.flavor(conn)

    if flv == 'mysql':
        sql = """
        INSERT INTO last_sync (dst, src, last_id) VALUES (:dst, :src, :last_id)
        ON DUPLICATE KEY UPDATE last_id = :last_id
        """
    elif flv == 'postgresql':
        sql = """
        INSERT INTO last_sync (dst, src, last_id) VALUES (:dst, :src, :last_id)
        ON CONFLICT (dst, src) DO UPDATE SET last_id = :last_id
        """
    else:
        raise Exception("Unsupporter SQL flavor: {}".format(flv))

    conn.execute(text(sql), dst=destination, src=source, last_id=last_id)
    return last_id

def zero_dt():
    return datetime(1, 1, 1)

def last_sync_dt(conn, dst, src):
    last_dt = conn.execute(
        text(
            """
            SELECT last_dt FROM last_sync_dt
            WHERE dst = :dst AND src = :src
            """
        ),
        dst=dst,
        src=src,
    ).fetchone()

    if last_dt is None:
        last_dt = zero_dt()
    else:
        last_dt = last_dt[0]

    return last_dt


def save_last_sync_dt(conn, destination, source, last_dt):
    runner = RunStatement()
    flv = runner.flavor(conn)

    if flv == 'mysql':
        sql = """
        INSERT INTO last_sync_dt (dst, src, last_dt) VALUES (:dst, :src, :last_dt)
        ON DUPLICATE KEY UPDATE last_dt = :last_dt
        """
    elif flv == 'postgresql':
        sql = """
        INSERT INTO last_sync_dt (dst, src, last_dt) VALUES (:dst, :src, :last_dt)
        ON CONFLICT (dst, src) DO UPDATE SET last_dt = :last_dt
        """
    else:
        raise Exception("Unsupporter SQL flavor: {}".format(flv))

    conn.execute(text(sql), dst=destination, src=source, last_dt=last_dt)
    return last_dt
