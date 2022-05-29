
class SillyDbError(Exception):
    pass


MIGRATE_ALL_ERROR = (
    "No migrations directory have been defined, do it when créating the "
    "database :\n"
    "db = DB(base=[some_dir], file=[some_file], migrations_dir=[THIS DIR]"
)
