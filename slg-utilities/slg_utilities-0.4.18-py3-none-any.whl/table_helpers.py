from tabulate import tabulate


# Create an html table easily with tabulate like so:

# from tabulate import tabulate
# tabulate(<your_data>, headers=<your_headers>, tablefmt="html")
# where <your_data> is of the form [[row1 data], [row2 data], ....etc]
# where <your_headers> is of the form [header1, header2, header3, ....etc]

# this will output clean html table
# helper for this defined below

# all supported table formats by tabulate
# "plain"
# "simple"
# "github"
# "grid"
# "fancy_grid"
# "pipe"
# "orgtbl"
# "jira"
# "presto"
# "pretty"
# "psql"
# "rst"
# "mediawiki"
# "moinmoin"
# "youtrack"
# "html"
# "latex"
# "latex_raw"
# "latex_booktabs"
# "textile"


def create_table_from_objects(
        objects, keys_as_headers, format='fancy_grid', **kwargs):
    '''
    <objects> is a list of python dicts
    <keys_as_headers> are the desired keys from the objects that you wish to display values for
    <format> is simply passed to tabulate (see above for all supported formats)
        common formats are : "html", "fancy_grid"

    pass any required optional kwargs to the tabulate function

    data is composed of rows so the naming is such

    return value is table in specified format

    if sorting is desired then it is probably easier to simply view in browser (local or not) by using Datatables
        because sorting can be applied to any field
    '''

    data = []
    for obj in objects:
        row = []
        for key in keys_as_headers:
            row.append(obj.get(key, ''))
        data.append(row)

    headers = keys_as_headers

    return tabulate(data, headers=headers, tablefmt=format, **kwargs)
