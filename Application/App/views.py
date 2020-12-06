from flask import render_template, request, abort
from flask.helpers import url_for
from markupsafe import Markup
from werkzeug.utils import redirect

from Application.models import db, TTN_User, Device, Service, Gateway, Connection
from Application.mqttconnect import start, get_data, client, check_username_valid
from Application.graphs import query_tables, create_plot, get_map
from Application import app


display = []


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', back_button=True, response='404 Page not found.')


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
    if request.method == 'POST':
        if request.form.get('submit_new_user'):
            new_username = request.form['new_username']
            new_passphrase = request.form['new_passphrase']
            new_broker = request.form['new_broker']
            new_topic = request.form['new_topic']

            start(new_username, new_passphrase, new_broker, new_topic)

            if check_username_valid() == False:
                report = f'User {new_username} does not exist in The Things Network. New user not saved. Register ' + \
                    Markup(
                        "<a href='https://account.thethingsnetwork.org/register' target='_blank'>Here</a>")

            elif check_username_valid() == True:
                if (TTN_User.query.filter(new_username == TTN_User.username).first()) is not None:
                    report = f'User {new_username} already exist.'
                    client.disconnect()
                else:

                    new_user = TTN_User(
                        username=new_username, password=new_passphrase, broker=new_broker, topic=new_topic)

                    try:
                        db.session.add(new_user)
                        db.session.commit()
                        report = f'New user: {new_username} added to database. You may now connect. ' + Markup(
                            "<a href='/'>CONNECT</a>")
                        client.disconnect()

                    except:
                        print("Error adding to table TTN_User.")
            else:
                report = 'There was an error in your request.'

            return render_template('index.html', adduser=True, back_button=True, new_username=new_username, new_passphrase=new_passphrase, new_broker=new_broker, new_topic=new_topic, report=report)
    else:
        return render_template('index.html', adduser=True, back_button=True)


@app.route('/startReceiving/', methods=['GET', 'POST'])
def start_receive():
    if request.method == 'GET':
        username = request.args.get('username')
        user_id = request.args.get('user_id')
        response = "Device is connected."

        global display
        display = get_data()

        return render_template('index.html', title='Device Page', refresh=True, success='success', username=username, user_id=user_id, response=response, device_info=display[0], service_info=display[1], gateway_info=display[2], connection_info=display[3], back_button=True)

    elif request.method == 'POST':
        if request.form.get('stop'):
            client.disconnect()

            return render_template('index.html', title='Device Page', success='success', stop_connect='disabled', device_info=display[0], service_info=display[1], gateway_info=display[2], connection_info=display[3], back_button=True)

        elif request.form.get('save'):
            user_id = request.args.get('user_id')

            return redirect(url_for('save_data', user_id=user_id))

    else:
        abort(404)


@app.route('/save/', methods=['GET', 'POST'])
def save_data():
    if len(display) > 0:
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

                    response = 'New data successfully saved to database.'

                    return render_template('index.html', title='Device Page', success='success', refresh=False, stop_connect='disabled', save_button='disabled', empty=True, response=response, back_button=True)

                except ValueError:
                    print("Error adding to table Connection.")
        else:
            response = 'Tables are empty. Could not save any data.'
            return render_template('index.html', title='Device Page', success='success', refresh=False, stop_connect='disabled', save_button='disabled', empty=True, response=response, back_button=True)

    else:
        abort(404)


@app.route('/visualizations/')
def visualize():
    return render_template('visualizations.html', title='Visualizations')


@app.route('/visualizations/<table_name>/')
def get_table(table_name):
    if table_name == 'Device' or table_name == 'Service' or table_name == 'Gateway' or table_name == 'Connection':

        return render_template('visualizations.html', title='Visualizations', active=table_name, table_name=table_name, show_drop_down=True, type_of_graph='Choose Type of Graph')

    else:
        abort(404)


@app.route('/visualizations/<table_name>/<graph>/')
@app.route('/visualizations/<table_name>/<graph>/<n>/', methods=['GET', 'POST'])
def show_graph(table_name, graph, n=1):

    df = query_tables(table_name, n)

    if graph == 'Line Plot':
        get_line_plot = create_plot(table_name, df)

        if get_line_plot == None:
            response = 'No plot for this table.'

            return render_template('visualizations.html', title='Visualizations', active=table_name, table_name=table_name, type_of_graph=graph, response=response, show_drop_down=True, n_dropdown=True, n=n)

        else:

            return render_template('visualizations.html', title='Visualizations', active=table_name, table_name=table_name, type_of_graph=graph, plot=get_line_plot, show_drop_down=True, n_dropdown=True, n=n)

    elif graph == 'Map':
        map_data = get_map(table_name, df)

        return render_template('visualizations.html', title='Visualizations', active=table_name, table_name=table_name, type_of_graph=graph, show_drop_down=True, n_dropdown=True, n=n, show_maps=True, map_data=map_data)

    elif graph == 'Table':

        table_cols = df.columns
        table_list = df.to_numpy(dtype=str)

        return render_template('visualizations.html', title='Visualizations', active=table_name, table_name=table_name, type_of_graph=graph, show_table=True, table_cols=table_cols, table_list=table_list, show_drop_down=True, n_dropdown=True, n=n)

    return render_template('visualizations.html', title='Visualizations', active=table_name, table_name=table_name, type_of_graph=graph, show_drop_down=True, n_dropdown=True)


@app.route('/update/<table_name>/<update_id>/', methods=['GET', 'POST'])
def update(table_name, update_id):

    if table_name == 'Device':
        update_data = Device.query.get_or_404(update_id)
        data_list = [update_data.dev_id, update_data.device_name, update_data.latitude,
                     update_data.longitude, update_data.altitude, update_data.location, update_data.user_id]
        col_list = Device.__table__.columns.keys()
        data_dict = dict(zip(col_list, data_list))

    elif table_name == 'Service':
        update_data = Service.query.get_or_404(update_id)
        data_list = [update_data.service_id, update_data.time, update_data.status, update_data.water_ml, update_data.countdown_timer,
                     update_data.water_counter, update_data.voltage_max, update_data.voltage_min, update_data.current_max, update_data.current_min, update_data.dev_id]
        col_list = Service.__table__.columns.keys()
        data_dict = dict(zip(col_list, data_list))

    elif table_name == 'Gateway':
        update_data = Gateway.query.get_or_404(update_id)
        data_list = [update_data.gateway_id, update_data.gtw_id, update_data.latitude,
                     update_data.longitude, update_data.altitude, update_data.location]
        col_list = Gateway.__table__.columns.keys()
        data_dict = dict(zip(col_list, data_list))

    elif table_name == 'Connection':
        update_data = Connection.query.get_or_404(update_id)
        data_list = [update_data.conn_id, update_data.gateway_id, update_data.service_id,
                     update_data.dev_id, update_data.rssi, update_data.snr]
        col_list = Connection.__table__.columns.keys()
        data_dict = dict(zip(col_list, data_list))

    else:
        abort(404)

    if request.method == 'POST':
        if table_name == 'Device':
            update_data.device_name = request.form['device_name']
            update_data.altitude = request.form['altitude']

        elif table_name == 'Service':
            update_data.water_ml = request.form['water_ml']

        elif table_name == 'Gateway':
            update_data.altitude = request.form['altitude']

        elif table_name == 'Connection':
            update_data.rssi = request.form['rssi']
            update_data.snr = request.form['snr']
        else:
            abort(404)
        try:
            db.session.commit()
            return render_template('update.html', title='Update', response=f'Successfully edited fields in {table_name}', data_dict=data_dict)
        except:
            return render_template('update.html', title='Update', response=f'Error editing the table {table_name}', data_dict=data_dict)
    else:
        return render_template('update.html', title='Update', table_name=table_name, data_dict=data_dict)


@ app.route('/visualizations/<table_name>/delete/<id>/')
def delete(table_name, id):

    id = int(id)

    if table_name == 'Device':
        to_delete = Device.query.get_or_404(id)

    elif table_name == 'Service':
        to_delete = Service.query.get_or_404(id)

    elif table_name == 'Gateway':
        to_delete = Gateway.query.get_or_404(id)

    elif table_name == 'Connection':
        to_delete = Connection.query.get_or_404(id)

    else:
        to_delete = ''

    try:
        db.session.delete(to_delete)
        db.session.commit()

        return render_template('visualizations.html', response='Data successfully deleted.')

    except:

        return render_template('visualizations.html', response='There was a problem deleting that task')
