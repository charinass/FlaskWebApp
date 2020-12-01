import plotly
import plotly.express as px
import plotly.graph_objs as graph_obj

import pandas as pd
import numpy as np
import json

from .models import db, Service


def create_plot():
    df = pd.DataFrame(db.session.query(
        Service.voltage_max,
        Service.voltage_min,
        Service.time).all(), columns=['Voltage Max [V]', 'Voltage Min [V]', 'Time'])

    print(df)

    fig1 = px.line(df, x='Time', y=[
                   'Voltage Max [V]', 'Voltage Min [V]'], title='Supply Voltage Graph')

    # N = 40
    # x = np.linspace(0, 1, N)
    # y = np.random.randn(N)
    # df = pd.DataFrame({'x': x, 'y': y})  # creating a sample dataframe

    # data = [
    #     graph_obj.Bar(
    #         x=df['x'],  # assign x as the dataframe column 'x'
    #         y=df['y']
    #     )
    # ]

    graph_in_json = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    return graph_in_json


def create_hist():
    pass


def get_map():
    pass


def get_table():
    pass
