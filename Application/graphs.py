import json
import pandas as pd
import plotly.express as px
import plotly


from .models import db, Service, Device, Gateway, Connection


def query_tables(table_name, n):

    if table_name == 'Device':
        if n == 'all':
            n = int(Device.query.filter(Device.dev_id).count())

        df = pd.DataFrame(db.session.query(
            Device.dev_id.label('Device ID'),
            Device.device_name.label('Device Name'),
            Device.latitude.label('Device Latitude'),
            Device.longitude.label('Device Longitude'),
            Device.altitude.label('Device Altitude'),
            Device.location.label('Device Location'),
            Device.user_id.label('User ID')
        ).limit(n).all())

        return df

    elif table_name == 'Service':
        if n == 'all':
            n = int(Service.query.filter(Service.service_id).count())

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
        ).limit(n).all())

        return df

    elif table_name == 'Gateway':
        if n == 'all':
            n = int(Gateway.query.filter(Gateway.gateway_id).count())

        df = pd.DataFrame(db.session.query(
            Gateway.gateway_id.label('Gateway ID'),
            Gateway.gtw_id.label('GTW ID'),
            Gateway.latitude.label('Gateway Latitude'),
            Gateway.longitude.label('Gateway Longitude'),
            Gateway.altitude.label('Gateway Altitude'),
            Gateway.location.label('Gateway Location')
        ).limit(n).all())

        return df

    elif table_name == 'Connection':
        if n == 'all':
            n = int(Connection.query.filter(Connection.conn_id).count())

        df = pd.DataFrame(db.session.query(
            Connection.conn_id.label('Connection ID'),
            Connection.gateway_id.label('Gateway ID'),
            Connection.service_id.label('Service ID'),
            Connection.dev_id.label('Device ID'),
            Connection.rssi.label('RSSI'),
            Connection.snr.label('SNR')
        ).limit(n).all())

        return df

    else:

        return pd.DataFrame()


def create_plot(table_name, df):

    graph_in_json = []

    if table_name == 'Service':
        fig = px.line(df, x='Time', y=[
            'Voltage Max [V]', 'Voltage Min [V]', 'Current Max', 'Current Min'])

        graph_in_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    elif table_name == 'Connection':
        fig = px.line(df, x='Connection ID', y=[
            'RSSI', 'SNR'])
        graph_in_json = json.dumps(
            fig, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        graph_in_json = None

    return graph_in_json


def get_map(table_name, df):
    if table_name == 'Device':
        return df['Device Location']

    elif table_name == 'Gateway':
        return df['Gateway Location']
