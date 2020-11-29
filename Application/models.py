from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='')
db = SQLAlchemy(app)


class TTN_User(db.Model):
    __tablename__ = 'TTN_User'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    broker = db.Column(db.String)
    topic = db.Column(db.String)

    def __repr__(self) -> str:
        return f'<TTN_User {self.user_id}>'


class Device(db.Model):
    __tablename__ = 'Device'
    dev_id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude = db.Column(db.Float)
    location = db.Column(db.String)
    user_id = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f'<Device {self.dev_id}>'


class Service(db.Model):
    __tablename__ = 'Service'
    service_id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String)
    status = db.Column(db.Integer)
    water_ml = db.Column(db.Integer)
    countdown_timer = db.Column(db.Integer)
    water_counter = db.Column(db.Integer)
    voltage_max = db.Column(db.Float)
    voltage_min = db.Column(db.Float)
    current_max = db.Column(db.Float)
    current_min = db.Column(db.Float)
    dev_id = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f'<Service {self.service_id}>'


class Gateway(db.Model):
    __tablename__ = 'Gateway'
    gateway_id = db.Column(db.Integer, primary_key=True)
    gtw_id = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude = db.Column(db.Float)
    location = db.Column(db.String)

    def __repr__(self) -> str:
        return f'<Gateway {self.gateway_id}>'


class Connection(db.Model):
    __tablename__ = 'Connection'
    conn_id = db.Column(db.Integer, primary_key=True)
    gateway_id = db.Column(db.Integer)
    service_id = db.Column(db.Integer)
    dev_id = db.Column(db.Integer)
    rssi = db.Column(db.Float)
    snr = db.Column(db.Float)

    def __repr__(self) -> str:
        return f'<Connection {self.conn_id}>'
