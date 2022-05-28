"""
# Plotly out of the box behavior

If you were to plot a bar chart in plotly, the out of the box behavior would be
this. Note that there are a lot of things in this chart that doesn't really
enhance the graph visualization.
"""
import cauldron as cd
import pandas as pd
import plotly.express as px

df: pd.DataFrame = cd.shared.report_data

cd.display.markdown(__doc__)

cd.display.table(df)

fig = px.bar(df, title='Exported Reports', x='name', y='exported')

cd.display.plotly(figure=fig)
