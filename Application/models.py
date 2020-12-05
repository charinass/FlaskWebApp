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
        return f"{self.user_id}, {self.username}, {self.password}, {self.broker}, {self.topic}"


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
        return f"{self.dev_id}, {self.device_name}, {self.latitude}, {self.longitude}, {self.altitude}, {self.location}, {self.user_id}"


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
        return f"{self.service_id}, {self.time}, {self.status}, {self.water_ml}, {self.countdown_timer}, {self.water_counter}, {self.voltage_max}, {self.voltage_min}, {self.current_max}, {self.current_min}, {self.dev_id}"


class Gateway(db.Model):
    __tablename__ = 'Gateway'
    gateway_id = db.Column(db.Integer, primary_key=True)
    gtw_id = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude = db.Column(db.Float)
    location = db.Column(db.String)

    def __repr__(self) -> str:
        return f"{self.gateway_id}, {self.gtw_id}, {self.latitude}, {self.longitude}, {self.altitude}, {self.location}"


class Connection(db.Model):
    __tablename__ = 'Connection'
    conn_id = db.Column(db.Integer, primary_key=True)
    gateway_id = db.Column(db.Integer)
    service_id = db.Column(db.Integer)
    dev_id = db.Column(db.Integer)
    rssi = db.Column(db.Float)
    snr = db.Column(db.Float)

    def __repr__(self) -> str:
        return f"{self.conn_id}, {self.gateway_id}, {self.service_id}, {self.dev_id}, {self.rssi}, {self.snr}"
