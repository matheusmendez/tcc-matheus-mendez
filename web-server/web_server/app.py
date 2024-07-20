from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from os import environ



# environ[
#     'DB_URL'
# ] = 'postgresql+psycopg2://admin:uea_est202401@localhost:5432/db_temp_humi'

# # environ['SECRET_KEY'] = 'uea_est'
# environ['MQTT_BROKER_URL'] = 'localhost'
# environ['MQTT_BROKER_PORT'] = '1883'

# print(f"url= {environ.get('MQTT_BROKER_URL')}")
# print(f"PORTA= {int(environ.get('MQTT_BROKER_PORT'))}")

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
    app.run(host='0.0.0.0', debug=True)
