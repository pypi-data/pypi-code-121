from django.db import connection
from django.db import reset_queries
from functools import wraps

def num_queries():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prefix = f"{func.__name__}: "

            reset_queries()
            result = func(*args, **kwargs)
            total_queries = len(connection.queries)

            print(f"{prefix} executed {total_queries} queries")

            return result
        return wrapper
    return decorator
