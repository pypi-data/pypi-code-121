#!/usr/bin/env python3

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Mapping, Optional

from grantme.constants.msgs import *
from grantme.constants.sqls import *
from grantme.utils.errors import *

from .utils import printers, timer


class Mode(Enum):
    EXCLUSIVE = auto()
    SHARED = auto()


@dataclass
class LockStatus:
    mode: Mode
    user_expires: Mapping[str, datetime]


@dataclass
class GrantResult:
    curr_mode: Optional[Mode]
    prev_mode: Optional[Mode]
    curr_expire_at: Optional[datetime]
    prev_expire_at: Optional[datetime]


def write_lock(who: str, mode: Mode, expire_at: datetime, conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        UPSERT,
        {"who": who, "shared": mode == Mode.SHARED, "expire_at": expire_at},
    )
    assert cur.rowcount == 1
    cur.close()


def get_status(conn: sqlite3.Connection) -> Optional[LockStatus]:
    now = datetime.now()

    cur = conn.cursor()
    cur.execute(QUERY_SHARED, {"now": now})
    rows = cur.fetchall()
    if len(rows) > 0:
        cur.close()
        return LockStatus(
            mode=Mode.SHARED,
            user_expires={row["user"]: row["expire_at"] for row in rows},
        )

    cur.execute(QUERY_EXCLUSIVE, {"now": now})
    row = cur.fetchone()
    if row is not None:
        cur.close()
        return LockStatus(
            mode=Mode.EXCLUSIVE, user_expires={row["user"]: row["expire_at"]}
        )

    cur.close()
    return None


def revoke(who, conn: sqlite3.Connection) -> Optional[Mode]:
    status = get_status(conn)

    if status is None:
        return None

    if who not in status.user_expires:
        return None

    cur = conn.cursor()
    cur.execute(RELEASE, {"who": who})
    assert cur.rowcount == 1
    cur.close()
    conn.commit()

    return status.mode


def grant(
    who: str, wanted: Mode, duration: str, conn: sqlite3.Connection
) -> GrantResult:
    attempted_expire = datetime.now() + timer.parse_delta(duration)

    status = get_status(conn)
    result = GrantResult(None, None, None, None)

    # Case 1: if no lock is granted, simply grant one
    if status is None:
        write_lock(who, wanted, attempted_expire, conn)
        conn.commit()

        result.curr_mode = wanted
        result.curr_expire_at = attempted_expire
        return result

    # Case 2: if neither s- nor x-locked, try lock
    if who not in status.user_expires:
        # cannot want shared when an exclusive is granted (not to `who`)
        # cannot want exclusive when any other lock is granted (not to `who`)
        if (wanted == Mode.SHARED and status.mode == Mode.EXCLUSIVE) or (
            wanted == Mode.EXCLUSIVE and len(status.user_expires) > 0
        ):
            raise GrantmeError(GRANT_FAILURE_MSG, GRANT_FAILURE_CODE)

        write_lock(who, wanted, attempted_expire, conn)
        conn.commit()

        result.curr_mode = wanted
        result.curr_expire_at = attempted_expire
        return result

    # Case 3: if already locked, try (upgrade and) prolong
    result.prev_mode = status.mode

    # prevent accidental downgrade
    if result.prev_mode == Mode.EXCLUSIVE and wanted == Mode.SHARED:
        wanted = Mode.EXCLUSIVE

    # try upgrade
    if result.prev_mode == Mode.SHARED and wanted == Mode.EXCLUSIVE:
        if len(status.user_expires) > 1:
            raise GrantmeError(UPGRADE_FAILURE_MSG, UPGRADE_FAILURE_CODE)

        cur = conn.cursor()
        cur.execute(UPGRADE, {"who": who})
        assert cur.rowcount == 1
        cur.close()

        result.curr_mode = Mode.EXCLUSIVE
    else:
        result.curr_mode = result.prev_mode

    # try prolong
    old_expire = status.user_expires[who]
    result.prev_expire_at = old_expire
    if old_expire > attempted_expire:
        result.curr_expire_at = old_expire
    else:
        write_lock(who, wanted, attempted_expire, conn)
        result.curr_expire_at = attempted_expire

    conn.commit()
    return result


def print_status(you: str, conn: sqlite3.Connection):
    status = get_status(conn)

    printers.show_sep_line()

    if status is None:
        printers.show_no_lock()
    elif status.mode == Mode.EXCLUSIVE:
        user, expire_at = next(iter(status.user_expires.items()))
        if user == you:
            printers.show_granted(
                "Exclusive", expire_at, highlighted_user=user + " (YOU)"
            )
        else:
            printers.show_granted("Exclusive", expire_at, others=[user])
            printers.warning(DO_NOT_DISTURB)
    else:
        last_expire = max(status.user_expires.values())
        if you in status.user_expires:
            others = list(status.user_expires.keys())
            others.remove(you)
            printers.show_granted(
                "Shared", last_expire, highlighted_user=you + " (YOU)", others=others
            )
            printers.show_expire(status.user_expires[you], "Your")
        else:
            printers.show_granted(
                "Shared", last_expire, others=status.user_expires.keys()
            )
            printers.slock_guide()

    printers.show_sep_line()


def revoke_and_print_result(who, conn: sqlite3.Connection):
    result = revoke(who, conn)
    if result is None:
        printers.warning(NOTHING_REVOKED)
    elif result == Mode.EXCLUSIVE:
        printers.show_revoke_ok("exclusive", who)
    else:
        printers.show_revoke_ok("shared", who)


def grant_and_print_result(
    who: str, want_shared: bool, duration: str, conn: sqlite3.Connection
):
    result = grant(who, Mode.SHARED if want_shared else Mode.EXCLUSIVE, duration, conn)

    # when called with a lock already held
    if result.prev_mode is not None:
        assert result.curr_mode is not None
        assert result.prev_expire_at is not None
        assert result.curr_expire_at is not None

        if result.prev_mode == Mode.EXCLUSIVE and want_shared:
            assert result.curr_mode == Mode.EXCLUSIVE
            printers.warning(ATTEMPT_SLOCK_WITH_XLOCK)

        if result.prev_mode == Mode.SHARED and result.curr_mode == Mode.EXCLUSIVE:
            printers.ok(UPGRADE_OK)

        if result.prev_expire_at == result.curr_expire_at:
            printers.warning(ATTEMPT_SHORTER_DURATION_THAN_ALREADY_GRANTED)
        else:
            printers.ok(PROLONG_OK)
        printers.show_expire(result.curr_expire_at, "Your")

    # when called without a lock already held
    else:
        if result.curr_mode is not None:
            assert result.prev_expire_at is None
            assert result.curr_expire_at is not None
            printers.show_grant_ok("shared" if want_shared else "exclusive", who)
            printers.show_expire(result.curr_expire_at, "Your")
