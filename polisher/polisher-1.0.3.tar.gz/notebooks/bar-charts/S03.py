import cauldron as cd
import pandas as pd
import plotly.graph_objects as go

import polisher

df: pd.DataFrame = cd.shared.report_data

GRAY = '#898989'

layout = go.Layout(
    title='Exported Reports',
    xaxis={'title':  {'text': 'name'}},
    yaxis={'title': {'text': 'exported'}},
)

fig = go.Figure(layout=layout)
fig.add_trace(go.Bar(x=df['name'], y=df['exported'], text=df['exported']))

cd.display.text('Remove grids')
fig = polisher.remove_grids(figure=fig)
cd.display.plotly(figure=fig)


cd.display.text('Remove background color')
fig = polisher.remove_background(figure=fig)
cd.display.plotly(figure=fig)


cd.display.text('Send to background')
fig = polisher.send_to_background(fig)
cd.display.plotly(figure=fig)

cd.display.text('Focus')
fig.update_traces(
    texttemplate='%{text:.2s}', textposition='inside', textfont_size=14
)
# fig = fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)
print(fig)
