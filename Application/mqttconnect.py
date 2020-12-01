import base64
import json
import requests
import struct
import paho.mqtt.client as mqtt


client = mqtt.Client()
TTN_USERNAME = ""
TTN_PASSWORD = ""
THE_BROKER = ""
THE_TOPIC = ""

device_info = {}
service_info = {}
gateway_info = {}
connection_info = {}


def on_connect(client, userdata, flags, rc):
    print("Connected to ", client._host, "port: ", client._port)
    print("Flags: ", flags, "return code: ", rc)
    client.subscribe(THE_TOPIC)


def on_message(client, userdata, msg):
    themsg = json.loads(msg.payload.decode("utf-8"))
    payload_plain = base64.b64decode(themsg["payload_raw"])
    gateway_link = "https://www.thethingsnetwork.org/gateway-data/gateway/{}"

    global_list = globals()
    # Device info
    device_name = themsg["dev_id"]
    device_latitude = themsg["metadata"].get("latitude", 0.0)
    device_longitude = themsg["metadata"].get("longitude", 0.0)
    device_altitude = themsg["metadata"].get("altitude", 0.0)
    device_location = (themsg["metadata"].get(
        "latitude", 0.0), themsg["metadata"].get("longitude", 0.0))
    device_info_list = [device_name, device_latitude,
                        device_longitude, device_altitude, device_location]
    device_titles = ['Device Name', 'Device Latitude',
                     'Device Longitude', 'Device Altitude', 'Device Location']
    global_list['device_info'] = dict(zip(device_titles, device_info_list))

    # Service info
    service_time = (themsg["metadata"]["time"][0:10],
                    themsg["metadata"]["time"][11:30])
    service_status = struct.unpack('B', payload_plain[0:1])[0]
    service_water_ml = struct.unpack('H', payload_plain[1:3])[0]
    service_countdown_timer = struct.unpack('I', payload_plain[9:13])[0]
    service_water_counter = struct.unpack('H', payload_plain[3:5])[0]
    service_voltage_max = struct.unpack('f', payload_plain[13:17])[0]
    service_voltage_min = struct.unpack('f', payload_plain[17:21])[0]
    service_current_max = struct.unpack('f', payload_plain[21:25])[0]
    service_current_min = struct.unpack('f', payload_plain[25:29])[0]
    service_info_list = [service_time, service_status, service_water_ml, service_countdown_timer,
                         service_water_counter, service_voltage_max, service_voltage_min, service_current_max, service_current_min]
    service_titles = ['Time', 'Status', 'Water (ml)', 'Countdown Timer',
                      'Water Counter', 'Voltage Max', 'Voltage Min', 'Current Max', 'Current Min']
    global_list['service_info'] = dict(zip(service_titles, service_info_list))

    # Gateway info
    num_of_gateways = len(themsg["metadata"]["gateways"])
    gateway_info_list = []
    connection_info_list = []
    gateway_titles = ['Gateway ID', 'Gateway Latitude',
                      'Gateway Longitude', 'Gateway Altitude', 'Gateway Location']
    connection_titles = ['RSSI', 'SNR']
    for gtw_number in range(num_of_gateways):
        gtw_id = themsg["metadata"]["gateways"][gtw_number]["gtw_id"]
        if gtw_id != None:
            requested_info = requests.get(gateway_link.format(gtw_id))
            gateway_location = requested_info.json()
            for each in gateway_location.values():
                if each.get('location', 0) == 0:
                    gtw_latitude = 0.0
                    gtw_longitude = 0.0
                    gtw_altitude = 0.0
                    gateway_info_list.append([gtw_id, gtw_latitude,
                                              gtw_longitude, gtw_altitude, (gtw_latitude, gtw_longitude)])
                else:
                    gtw_latitude = each['location'].get('latitude', 0.0)
                    gtw_longitude = each['location'].get('longitude', 0.0)
                    gtw_altitude = each['location'].get('altitude', 0.0)
                    gateway_info_list.append([gtw_id, gtw_latitude,
                                              gtw_longitude, gtw_altitude, (gtw_latitude, gtw_longitude)])
        global_list['gateway_info'][gtw_number] = dict(
            zip(gateway_titles, gateway_info_list[gtw_number]))

        # Connection info
        connection_rssi = themsg["metadata"]["gateways"][gtw_number]["rssi"]
        connection_snr = themsg["metadata"]["gateways"][gtw_number]["snr"]
        connection_info_list.append([connection_rssi, connection_snr])
        global_list['connection_info'][gtw_number] = dict(
            zip(connection_titles, connection_info_list[gtw_number]))

    print(
        f"number of gateways: {num_of_gateways}, \ndevice information: {device_info}, \nservice information: {service_info}, \ngateway information: {gateway_info}, \nconnection information: {connection_info}")


def get_data():
    '''returns the globals for views.py'''
    return [device_info, service_info, gateway_info, connection_info]


def start(username, password, broker, topic):
    global TTN_USERNAME, TTN_PASSWORD, THE_BROKER, THE_TOPIC
    TTN_USERNAME = username
    TTN_PASSWORD = password
    THE_BROKER = broker
    THE_TOPIC = topic
    client.username_pw_set(TTN_USERNAME, password=TTN_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(THE_BROKER, 1883, 60)
    client.loop_start()
