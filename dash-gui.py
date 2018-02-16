
import numpy as np
import plotly.plotly as plotly
import plotly.tools as tls
import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
freq = np.linspace(10, 100e3, 100)


def new_mag(): return [x for x in np.random.rand(len(freq))]

mag = new_mag()

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children="Plotly/Dash Test"),

    html.Div(children='''
        Some sort of subtitle
        '''),

    html.Button('Play', id='play'),

    dcc.Graph(
        id='example-graph',
        figure={
                'data': [{'x': freq, 'y': mag,
                          'type': 'line',
                          'name': 'Test plot'}],
                'layout': {'title': 'Tester'}
               },
        # animate=True
         ),

    dcc.Interval(id='interval', interval=100, n_intervals=0)

    ])


@app.callback(
    Output(component_id='example-graph', component_property='figure'),
    [Input(component_id='interval', component_property='n_intervals')])
def update_plot(nn):
    return {'data': [{'y': new_mag()}]}

# while range(100):
#     mag = new_mag


# plotly.newPlot('Test', )

if __name__ == '__main__':
    app.run_server(debug=True)

    # var data = [{
    #     x: ['VALUE 1'], // in reality I have more values...
    #     y: [20],
    #     type: 'bar'
    # }];
    # Plotly.newPlot('PlotlyTest', data);

    # function adjustValue1(value)

    #     Plotly.restyle('PlotlyTest', 'y', [[value]]);
