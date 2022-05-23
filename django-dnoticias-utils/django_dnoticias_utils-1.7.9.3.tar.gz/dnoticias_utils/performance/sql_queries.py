from django.db import connection
from django.db import reset_queries
from functools import wraps

def sql_queries():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prefix = f"{func.__name__}: "

            reset_queries()
            result = func(*args, **kwargs)

            queries = connection.queries

            print(f"{prefix} queries:")

            for query in queries:
                print(f"SQL: {query['sql']}")
                print(f"Took: {query['time']}")
            return result
        return wrapper
    return decorator
