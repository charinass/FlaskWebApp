import plotly
import plotly.express as px
import plotly.graph_objs as graph_obj

import pandas as pd
import numpy as np
import json

from .models import db, Service, Device, Gateway, Connection


def query_tables(table_name):
    if table_name == 'Device':
        df = pd.DataFrame(db.session.query(
            Device.dev_id.label('Device ID'),
            Device.device_name.label('Device Name'),
            Device.latitude.label('Device Latitude'),
            Device.longitude.label('Device Longitude'),
            Device.altitude.label('Device Altitude'),
            Device.location.label('Device Location'),
            Device.user_id.label('User ID')
        ))

        return df

    elif table_name == 'Service':
        df = pd.DataFrame(db.session.query(
            Service.service_id.label('Service ID'),
            Service.time.label('Time'),
            Service.status.label('Status'),
            Service.water_ml.label('Water (mL)'),
            Service.countdown_timer.label('Countdown Timer'),
            Service.water_counter.label('Water Counter'),
            Service.voltage_max.label('Voltage Max [V]'),
            Service.voltage_min.label('Voltage Min [V]'),
            Service.current_max.label('Current Max'),
            Service.current_min.label('Current Min')
        ))

        return df

    elif table_name == 'Gateway':
        df = pd.DataFrame(db.session.query(
            Gateway.gateway_id.label('Gateway ID'),
            Gateway.gtw_id.label('GTW ID'),
            Gateway.latitude.label('Gateway Latitude'),
            Gateway.longitude.label('Gateway Longitude'),
            Gateway.altitude.label('Gateway Altitude'),
            Gateway.location.label('Gateway Location')
        ))

        return df

    elif table_name == 'Connection':
        df = pd.DataFrame(db.session.query(
            Connection.conn_id.label('Connection ID'),
            Connection.gateway_id.label('Gateway ID'),
            Connection.service_id.label('Service ID'),
            Connection.dev_id.label('Device ID'),
            Connection.rssi.label('RSSI'),
            Connection.snr.label('SNR')
        ))

        return df

    else:

        return pd.DataFrame()


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
    df = pd.DataFrame(db.session.query(
        Device.location,
        Gateway.location).all(), columns=['Device Location', 'Gateway Location'])
    print(df)
    return df['Device Location'][5]


def get_table():
    pass
