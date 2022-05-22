import os
import sys
from logging import Logger, getLogger
from configparser import ConfigParser

from .utils import get_checksum

log: Logger = getLogger(__name__)


# db class that works for both html and md files
class Database:
    __OLD_COLUMN_NUM: int = 4
    __COLUMN_NUM: int = 5

    def __init__(self, db_path: str,
                 config: ConfigParser):
        log.debug('initializing the page db on path "%s"', db_path)
        self.db_path: str = db_path
        self.config: ConfigParser = config
        self.e: dict[str, tuple[float, float, str, list[str]]] = dict()


    # updates the tags for a specific entry (file)
    #   file_name only contains the entry name (without the absolute path)
    def update_tags(self, file_name: str,
                    tags: list[str]) -> None:
        if file_name in self.e:
            log.debug('updating tags for entry "%s"', file_name)
            cts, mts, checksum, old_tags = self.e[file_name]
            log.debug('entry "%s" old content: (%s, %s, %s, (%s))',
                      file_name, cts, mts, checksum, ', '.join(old_tags))
            self.e[file_name] = (cts, mts, checksum, tags)
            log.debug('entry "%s" new content: (%s, %s, %s, (%s))',
                      file_name, cts, mts, checksum, ', '.join(tags))
        else:
            log.error('can\'t update tags for entry "%s",'
                      ' as it is not present in db', file_name)
            sys.exit(1)


    # returns a bool that indicates if the entry
    # was (includes new entries) or wasn't updated
    def update(self, file_name: str,
               remove: str=None) -> bool:
        log.debug('updating entry for file "%s"', file_name)
        # initial default values
        f: str = file_name
        tags: list[str] = []
        if remove is not None:
            f = file_name.replace(remove, '')
            log.debug('removed "%s" from "%s": "%s"', remove, file_name, f)

        # get current time, needs actual file name
        time: float = os.stat(file_name).st_mtime
        log.debug('modified time for "%s": %s', file_name, time)

        # calculate current checksum, also needs actual file name
        checksum: str = get_checksum(file_name)
        log.debug('current checksum for "%s": "%s"', file_name, checksum)

        # two cases, 1) entry didn't exist,
        # 2) entry has been mod and,
        # 3) entry hasn't been mod
        #1)
        if f not in self.e:
            log.debug('entry "%s" didn\'t exist, adding with defaults', f)
            self.e[f] = (time, 0.0, checksum, tags)
            return True

        old_time, old_mod_time, old_checksum, tags = self.e[f]
        log.debug('entry "%s" old content: (%s, %s, %s, (%s))',
                  f, old_time, old_mod_time, old_checksum, ', '.join(tags))

        # 2)
        if checksum != old_checksum:
            if old_mod_time == 0.0:
                log.debug('entry "%s" has been modified for the first'
                          ' time, updating', f)
            else:
                log.debug('entry "%s" has been modified, updating', f)
            self.e[f] = (old_time, time, checksum, tags)
            log.debug('entry "%s" new content: (%s, %s, %s, (%s))',
                      f, old_time, time, checksum, ', '.join(tags))
            return True
        # 3)
        else:
            log.debug('entry "%s" hasn\'t been modified', f)
            return False


    def write(self) -> None:
        log.debug('writing db')
        with open(self.db_path, 'w') as file:
            for k, v in self.e.items():
                log.debug('parsing row for page "%s"', k)
                t: str = None
                row: str = None
                if len(v[3]) == 0:
                    t = '-'
                else:
                    t = ','.join(v[3])

                row = f'{k} {v[0]} {v[1]} {v[2]} {t}'

                log.debug('writing row: "%s\\n"', row)
                file.write(f'{row}\n')


    def _db_path_exists(self) -> bool:
        log.debug('checking that "%s" exists or is a file', self.db_path)
        if not os.path.exists(self.db_path):
            log.warning('"%s" doesn\'t exist, will be'
                        ' created once process finishes,'
                        ' ignore if it\'s the first run', self.db_path)
            return False

        if not os.path.isfile(self.db_path):
            log.error('"%s" is not a file"', self.db_path)
            sys.exit(1)

        return True


    def _read_raw(self) -> list[str]:
        rows: list[str] = None
        with open(self.db_path, 'r') as file:
            rows = file.readlines()
        log.debug('db contains %d rows', len(rows))

        return rows


    def read_old(self) -> None:
        log.debug('reading db with old schema (%d columns)', self.__OLD_COLUMN_NUM)
        if not self._db_path_exists():
            log.error('db path "%s" desn\'t exist, --add-checksum-to-db should'
                      'only be used when updating the old db schema', self.db_path)
            sys.exit(1)

        rows: list[str] = self._read_raw()
        cols: list[str] = None
        # l=list of values in entry
        log.debug('parsing rows from db')
        for it, row in enumerate(rows):
            i: int = it + 1
            r: str = row.strip()
            log.debug('row %d content: "%s"', i, r)
            # (file_name, ctimestamp, mtimestamp, [tags])
            cols: tuple[str, float, float, list[str]] = tuple(r.split())
            col_num: int = len(cols)
            if col_num != self.__OLD_COLUMN_NUM:
                log.critical('row %d doesn\'t contain %s columns, contains %d'
                             ' columns: "%s"',
                             i, self.__OLD_COLUMN_NUM, col_num, r)
                sys.exit(1)

            t: list[str] = None
            if cols[3] == '-':
                t = []
            else:
                t = cols[3].split(',')
            log.debug('tag content: (%s)', ', '.join(t))
            file_path: str = os.path.join(self.config.get('path', 'src'), cols[0])
            checksum: str = get_checksum(file_path)
            log.debug('checksum for "%s": "%s"', file_path, checksum)

            self.e[cols[0]] = (float(cols[1]), float(cols[2]), checksum, t)



    def read(self) -> None:
        log.debug('reading db')
        if not self._db_path_exists():
            return

        rows: list[str] = self._read_raw()
        cols: list[str] = None
        # l=list of values in entry
        log.debug('parsing rows from db')
        for it, row in enumerate(rows):
            i: int = it + 1
            r: str = row.strip()
            log.debug('row %d content: "%s"', i, r)
            # (file_name, ctimestamp, mtimestamp, checksum, [tags])
            cols: tuple[str, float, float, str, list[str]] = tuple(r.split())
            col_num: int = len(cols)
            if col_num == self.__OLD_COLUMN_NUM:
                log.error('row %d contains %d columns: "%s"; this is probably'
                          ' because of missing checksum column, which is used'
                          ' now to also check if a file has changed. Rerun'
                          ' with flag --add-checksum-to-db to add the checksum'
                          ' column to the current db; if you did any changes'
                          ' since last timestamp in db, it won\'t update'
                          ' modification timestamp',
                          i, self.__OLD_COLUMN_NUM, r)
                sys.exit(1)

            if col_num != self.__COLUMN_NUM:
                log.critical('row %d doesn\'t contain %s columns, contains %d'
                             ' columns: "%s"',
                             i, self.__COLUMN_NUM, col_num, r)
                sys.exit(1)

            t: list[str] = None
            if cols[4] == '-':
                t = []
            else:
                t = cols[4].split(',')
            log.debug('tag content: (%s)', ', '.join(t))

            self.e[cols[0]] = (float(cols[1]), float(cols[2]), cols[3], t)
