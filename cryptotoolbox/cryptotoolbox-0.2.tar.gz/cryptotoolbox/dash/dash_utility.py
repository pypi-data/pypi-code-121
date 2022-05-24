import dash_html_components as html


def format_percent_value(value):
    return f'{round(value, 2)}%'

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(format_percent_value(dataframe.iloc[i][col])) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])