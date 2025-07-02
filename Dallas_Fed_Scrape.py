import requests
from io import BytesIO
import pandas as pd
import numpy as np
import datetime
import plotly
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

def get_data(url):
	r = requests.get(url)
	url_content = r.content
	data = BytesIO(url_content)
	data_pd = pd.read_csv(data)
	return data_pd

national_url = "https://dallasfed.org/~/media/documents/research/mei/MEI_national_scaled_weekly.csv"
us_mobility = get_data(national_url)
state_url = "https://dallasfed.org/~/media/documents/research/mei/MEI_states_scaled_weekly.csv"
state_mobility = get_data(state_url)
#state_mobility = state_mobility.drop(columns = ['AK', 'HI'])

us_mobility['Time'] = pd.to_datetime(us_mobility['Time'])
state_mobility['Time'] = pd.to_datetime(state_mobility['Time'])

us_mobility_plt = go.Scatter(
                x = us_mobility['Time'],
                y = us_mobility['SDindex'],
                name = 'US Mobility',
                mode = 'lines'
    )

us_mb = go.Figure(data = us_mobility_plt)

us_mb.update_layout(
     title_text = 'Dallas Federal Reserve  US Mobility',
 )

data_slider = []
for week in state_mobility['Time'].unique():
    df_segmented =  state_mobility[(state_mobility['Time']== week)]

    heat_map = []
    for col in df_segmented.columns:
        #df_segmented[col] = df_segmented[col].astype(str)
        if col == 'Time':
            continue
        else:
            heat_map.append([col, np.int(df_segmented[col])])

    heat_map = pd.DataFrame(heat_map)
    heat_map.columns = ['State', "Mobility"]

    data_each_wk = dict(
                        type='choropleth',
                        locations = heat_map['State'],
                        z=heat_map['Mobility'],
                        locationmode='USA-states',
                        colorscale = 'Greens',
                        colorbar= {'title':'Mobility'})

    data_slider.append(data_each_wk)

steps = []
for i in range(len(data_slider)):
    step = dict(method='restyle',
                args=['visible', [False] * len(data_slider)],
                label='Week {}'.format(i))
    step['args'][1][i] = True
    steps.append(step)

sliders = [dict(active=0, pad={"t": 1}, steps=steps)]

layout = dict(title ='Dallas Fed Mobility', geo=dict(scope='usa',
                       projection={'type': 'albers usa'}),
              sliders=sliders)

df_hm = dict(data=data_slider, layout=layout)

app = dash.Dash(__name__)

app.layout = html.Div(children=[html.H1(children=''),
                        dcc.Graph(
                                id = 'Dallas Fed Mobility',
                                figure=us_mb
                            ),
                        html.H2(children=''),
                        dcc.Graph(
                                id = 'Heat Map',
                                figure=df_hm
                            )
                            ])


if __name__ == '__main__':
    app.run_server(debug=True)
