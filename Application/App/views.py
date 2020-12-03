from flask import render_template, request
from flask.helpers import url_for
from markupsafe import Markup
from werkzeug.utils import redirect

from Application.models import db, TTN_User, Device, Service, Gateway, Connection
from Application.mqttconnect import start, get_data, client, return_message
from Application.graphs import query_tables, create_plot, get_map
from Application import app


display = []


@app.route('/', methods=['GET', 'POST'])
def index():
    client.disconnect()
    if request.method == 'POST':
        userpass = request.form['userpass']
        if (TTN_User.query.filter(userpass == TTN_User.username).scalar() is not None):
            query_result = TTN_User.query.filter(
                userpass == TTN_User.username).first()

            start(query_result.username, query_result.password,
                  query_result.broker, query_result.topic)

            return redirect(url_for('start_receive', username=query_result.username, user_id=query_result.user_id))
        else:
            response = "Device does not exist."
            return render_template('index.html', title='Home', response=response)
    else:
        return render_template('index.html', title='Home')


@app.route('/addUser/', methods=['GET', 'POST'])
def add_user():
    client.disconnect()
    if request.method == 'POST':
        if request.form.get('submit_new_user'):
            new_username = request.form['new_username']
            new_passphrase = request.form['new_passphrase']
            new_broker = request.form['new_broker']
            new_topic = request.form['new_topic']

            start(new_username, new_passphrase,
                  new_broker, new_topic)

            if return_message() == False:
                report = f'User {new_username} does not exist in The Things Network. New user not saved. Register ' + \
                    Markup(
                        "<a href='https://account.thethingsnetwork.org/register' target='_blank'>Here</a>")
            else:
                if (TTN_User.query.filter(new_username == TTN_User.username).first()) is not None:
                    report = f'User {new_username} already exist.'
                    client.disconnect()

                else:

                    new_user = TTN_User(
                        username=new_username, password=new_passphrase, broker=new_broker, topic=new_topic)

                    try:
                        db.session.add(new_user)
                        db.session.commit()
                    except:
                        print("Error adding to table TTN_User.")

                    report = f'New user: {new_username} added to database. You may now connect. ' + Markup(
                        "<a href='/'>CONNECT</a>")

            return render_template('index.html', adduser=True, back_button=True, new_username=new_username, new_passphrase=new_passphrase, new_broker=new_broker, new_topic=new_topic, report=report)

    return render_template('index.html', adduser=True, back_button=True)


@app.route('/startReceiving', methods=['GET', 'POST'])
def start_receive():
    if request.method == 'GET':
        username = request.args.get('username')
        user_id = request.args.get('user_id')
        response = "Device is connected."

        global display
        display = get_data()

        return render_template('index.html', title='Device Page', refresh=True, success='success', username=username, user_id=user_id, response=response, device_info=display[0], service_info=display[1], gateway_info=display[2], connection_info=display[3])

    elif request.method == 'POST':
        if request.form.get('stop'):
            client.disconnect()

            return render_template('index.html', title='Device Page', success='success', stop_connect='disabled', device_info=display[0], service_info=display[1], gateway_info=display[2], connection_info=display[3])

        elif request.form.get('save'):
            user_id = request.args.get('user_id')

            return redirect(url_for('save_data', user_id=user_id))

        elif request.form.get('stop_back'):
            client.disconnect()

            return redirect('/')


@ app.route('/save', methods=['GET', 'POST'])
def save_data():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        client.disconnect()

        if display != [{}, {}, {}, {}]:
            # Query device name
            query_device = Device.query.filter_by(
                device_name=display[0]['Device Name']).first()

            # Tables
            new_device_data = Device(device_name=display[0]['Device Name'],
                                     latitude=display[0]['Device Latitude'],
                                     longitude=display[0]['Device Longitude'],
                                     altitude=display[0]['Device Altitude'],
                                     location=str(
                                         display[0]['Device Location']),
                                     user_id=user_id)

            new_service_data = Service(time=str(display[1]['Time']),
                                       status=display[1]['Status'],
                                       water_ml=display[1]['Water (ml)'],
                                       countdown_timer=display[1]['Countdown Timer'], water_counter=display[1]['Water Counter'],
                                       voltage_max=display[1]['Voltage Max'],
                                       voltage_min=display[1]['Voltage Min'],
                                       current_max=display[1]['Current Max'],
                                       current_min=display[1]['Current Min'])

            new_gateway_data = Gateway()
            new_connection_data = Connection()

            # Enter new data to table
            if query_device == None:
                try:
                    db.session.add(new_device_data)
                    db.session.commit()
                except ValueError:
                    print("Error adding to table Device.")

                new_service_data.dev_id = new_device_data.dev_id

                try:
                    db.session.add(new_service_data)
                    db.session.commit()
                except ValueError:
                    print("Error adding to table Service.")

                new_connection_data.dev_id = new_device_data.dev_id
                new_connection_data.service_id = new_service_data.service_id

            else:

                new_service_data.dev_id = query_device.dev_id
                new_connection_data.dev_id = query_device.dev_id

                try:
                    db.session.add(new_service_data)
                    db.session.commit()
                except ValueError:
                    print("Error adding to table Service.")

                new_connection_data.service_id = new_service_data.service_id

            for each in display[2].values():
                # Query Gateway gtw_id
                query_gateway_data = Gateway.query.filter_by(
                    gtw_id=each['Gateway ID']).first()
                if Gateway.query.filter_by(gtw_id=each['Gateway ID']).scalar() is None:
                    new_gateway_data.gtw_id = each['Gateway ID']
                    new_gateway_data.latitude = each['Gateway Latitude']
                    new_gateway_data.longitude = each['Gateway Longitude']
                    new_gateway_data.altitude = each['Gateway Altitude']
                    new_gateway_data.location = str(each['Gateway Location'])

                    try:
                        db.session.add(new_gateway_data)
                        db.session.commit()
                    except ValueError:
                        print("Error adding to table Gateway.")

                    new_connection_data.gateway_id = new_gateway_data.gateway_id

                else:
                    new_connection_data.gateway_id = query_gateway_data.gateway_id

            for each in display[3].values():
                new_connection_data.rssi = each['RSSI']
                new_connection_data.snr = each['SNR']
                try:
                    db.session.add(new_connection_data)
                    db.session.commit()
                except ValueError:
                    print("Error adding to table Connection.")
        else:
            response = 'Tables are empty. Could not save any data.'
            return render_template('index.html', title='Device Page', success='success', refresh=False, stop_connect='disabled', save_button='disabled', empty=True, response=response)

    elif request.form.get('stop_back'):
        client.disconnect()
        return redirect('/')


@ app.route('/visualizations/')
def visualize():
    return render_template('visualizations.html', title='Visualizations')


@app.route('/visualizations/<table_name>')
def get_table(table_name):
    df = query_tables(table_name)
    print(df)
    if df.empty:
        return render_template('visualizations.html', title='Visualizations', response='Table does not exist.')

    else:
        df_column_names = df.columns
        df_table = df.to_numpy(dtype=str)

        return render_template('visualizations.html', title='Visualizations', active=table_name, df_column_names=df_column_names, df_table=df_table)


@ app.route('/visualizations/<table_name>/<graph>', methods=['GET', 'POST'])
def show_graph(graph):
    if graph == 'line_graph':
        get_line_plot = create_plot()

        return render_template('visualizations.html', title='Visualizations', graph_type='Line Graph', plot=get_line_plot)
    elif graph == 'map_graph':
        get_map_data = get_map()
        return render_template('visualizations.html', title='Visualizations', graph_type='Location', show_maps=True, map_data=get_map_data)
