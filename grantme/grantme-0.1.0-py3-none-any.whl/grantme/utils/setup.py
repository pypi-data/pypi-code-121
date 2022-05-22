import platform
import sqlite3
from pathlib import Path

from grantme.constants.misc import PROG
from grantme.constants.sqls import CREATE_DB, CREATE_INDEX
from grantme.utils.printers import info


UPDATE_MOTD_DIR = Path("/etc/update-motd.d")


def create_motd():
    if "ubuntu" not in platform.version().lower():
        info(
            "Not running Ubuntu distributions, skipping creating the update-motd"
            " fragment."
        )
        return

    existing_frag_nums = {
        path.name[:2] for path in Path("/etc/update-motd.d").iterdir()
    }

    for i in range(99, -1, -1):
        i_str = f"{i:02}"
        if i_str in existing_frag_nums:
            continue

        motd_frag_name = f"{i_str}-grantme-status"
        motd_frag_file = UPDATE_MOTD_DIR / motd_frag_name
        with open(str(motd_frag_file), "w") as f:
            f.writelines(["#!/bin/sh\n", "echo\n", f"{PROG} --status\n"])

        # make new MOTD fragment executable
        motd_frag_file.chmod(motd_frag_file.stat().st_mode | 0o111)

        break


def create_db(data_dir: Path, db_file: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    setup_db(conn)
    conn.close()

    # make db accessible to everyone
    data_dir.chmod(data_dir.stat().st_mode | 0o666)
    db_file.chmod(db_file.stat().st_mode | 0o666)


def setup_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(CREATE_DB)
    cur.execute(CREATE_INDEX)
    cur.close()
    conn.commit()
