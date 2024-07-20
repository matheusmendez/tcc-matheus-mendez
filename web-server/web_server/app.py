from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from os import environ

DEBUG = bool(int(environ.get('DEBUG')))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['MQTT_BROKER_URL'] = environ.get('MQTT_BROKER_URL')
app.config['MQTT_BROKER_PORT'] = int(environ.get('MQTT_BROKER_PORT'))
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False


MQTT_SENSOR_TOPIC = 'sensores/medidas'
MQTT_CONFIG_TOPIC = 'sensores/config'

socketio = SocketIO(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mqtt = Mqtt(app, connect_async=True)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe(MQTT_SENSOR_TOPIC)


from views_device import *
from views_user import *

from models import create_database

create_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)
