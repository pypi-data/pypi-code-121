from django.db import models


"""Collection of database functions (mostly postgres specific)"""


class Epoch(models.Func):
    """
    Postgres function to extract the epoch (i.e. seconds) from an interval.
    """

    function = 'EXTRACT'
    template = "%(function)s('epoch' from %(expressions)s)"


class NormalizeUmlauts(models.Func):
    """
    Function to replace german umlauts in strings ('ä' -> 'ae'...).
    """

    arity = 1

    def __int__(self, expression, output_field=None):
        output_field = output_field or models.TextField()
        super().__init__(expression, output_field)

    @property
    def template(self):
        replacements = [('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('Ä', 'Ae'), ('Ö', 'Oe'), ('Ü', 'Ue'), ('ß', 'ss')]
        template = 'REPLACE(' * len(replacements) + '%(expressions)s'
        for umlaut, replacement in replacements:
            template += f", '{umlaut}', '{replacement}')"
        return template


class RegexpReplace(models.Func):
    """
    Postgres function to substitute text using regular expressions.
    """

    function = 'REGEXP_REPLACE'

    def __init__(self, expression, pattern, replacement=models.Value(''), flags=models.Value(''), **extra):
        super().__init__(expression, pattern, replacement, flags, **extra)


class SubquerySum(models.Subquery):
    """
    Useful for subquery-sum aggregations in query annotations:
    Requires a subquery, column name and output_field type.
    """

    template = '(SELECT sum(_sum."%(column)s") FROM (%(subquery)s) _sum)'

    def __init__(self, queryset, column, output_field=None, **extra):
        super().__init__(queryset, output_field, column=column, **extra)
