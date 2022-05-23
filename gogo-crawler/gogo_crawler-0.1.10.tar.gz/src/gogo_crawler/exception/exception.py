from sqlite3 import DatabaseError


def exception_handler(func):
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            print(f"{func.__name__} invalid arguemnt type")
        except DatabaseError as dberr:
            print(f"{func.__name__} database error found" + " error {0}".format(dberr))

    return inner_function
