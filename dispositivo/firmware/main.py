"""Firmware desenvolvido para o dispositivo de medição de temperatura e umidade, dispositvo que compõe o projeto de conlusão de curso: Desenvolvimento de um sistema de monitoramento de temperatura e umidade para fábrica de eletrônicos do polo industrial de Manaus."""

# Módulos padrão do MicroPython
from time import time, sleep
import dht
import network
import json
import machine
from machine import Pin, SoftI2C
from umqtt.simple import MQTTClient

# Classe local
from lcd_i2c import LcdI2c


class Config:
    """Implementa a classe de armazenamento de todas as variáveis de configuração do projeto."""
    def __init__(self) -> None:
        self._CONFIG_PATH = '/config/config.json'
        self._BASIC_CONFIG = {
            'WIFI_SSID': 'ssid',
            'WIFI_PASSWORD': 'password',
            'MQTT_BROKER': 'ip',
            'MQTT_CLIENT': 'sensor_drybox',
            'MQTT_SENSOR_TOPIC': 'sensores/medidas',
            'MQTT_CONFIG_TOPIC': 'sensores/config',
            'MAC_ADDRESS': 'FFFFFFFFFFFF',
            'TEMP_LIMIT_LOWER': 10.0,
            'TEMP_LIMIT_UPPER': 23.0,
            'TEMP_SETTING': 0.0,
            'HUMI_LIMIT_LOWER': 0.0,
            'HUMI_LIMIT_UPPER': 10.0,
            'HUMI_SETTING': 0.0,
            'DELAY_MEASURE': 20,
            'DELAY_BUZZER_ON': 15,
            'DELAY_BUZZER_OFF': 60,
        }
        self._config = None
        self._load_config()

    def _verify_keys(self, config: dict) -> bool:
        """Verifica se o objeto de configuração possui todos os parâmetros necessários."""
        for key in self._BASIC_CONFIG.keys():
            if key not in config.keys():
                return False
        return True

    def _load_attr(self) -> None:
        """Adiciona atributos de classe de acordo com o objeto de configuração."""
        for key, value in self._config.items():
            setattr(self, key, value)

    def _save_default(self) -> None:
        """Salva o objeto de configuração padrão."""
        with open(self._CONFIG_PATH, 'w') as f:
            f.write(json.dumps(self._BASIC_CONFIG, indent=4))
        self._config = self._CONFIG_PATH.copy()
        self._load_attr()

    def update(self, config: dict = None) -> None:
        """Salva um objeto de configuração."""
        if isinstance(config, dict) and config:
            self._config.update(config)
            with open(self._CONFIG_PATH, 'w') as f:
                f.write(json.dumps(self._config))
            self._load_attr()

    def _load_config(self) -> None:
        """Faz a leitura de um arquivo json para obter um objeto de configuração."""
        try:
            with open(self._CONFIG_PATH, 'r') as f:
                config = json.loads(f.read())
            if not self._verify_keys(config):
                self._save_default()
            else:
                self._config = config
                self._load_attr()
        except Exception as e:
            print(e)
            self._save_default()

    def __str__(self) -> str:
        """Representa o objeto como texto."""
        return f'{ {k:v for k,v in self._config.items()} }'


class Lcd:
    """Implementa a classe de LCD I2C."""
    def __init__(self) -> None:
        self._I2C_ADDR = 0x27
        self._I2C_ROWS = 2
        self._I2C_COLUMS = 16
        self._i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=800000)
        self._lcd = LcdI2c(
            self._i2c, self._I2C_ADDR, self._I2C_ROWS, self._I2C_COLUMS
        )

    def clear(self) -> None:
        """Limpa a tela do LCD."""
        self._lcd.clear()

    def write(self, message: str = '') -> None:
        """Escreve uma mensagem no LCD."""
        self._lcd.putstr(message)

    def write_data(self, data: dict) -> None:
        """Escreve a informação de um objeto no LCD."""
        self.clear()
        self.write(
            f'Temp: {data["temp_value"]:.2f} \xDFC  Humi: {data["humi_value"]:.2f} %'
        )

    def __str__(self) -> str:
        """Representa o objeto como texto."""
        return f'Lcd(addr={self._I2C_ADDR}, rows={self._I2C_ROWS},cols={self._I2C_COLUMS})'


class Sensor:
    """Implementa a classe de Sensor DHT22."""
    def __init__(self, config: Config) -> None:
        self._PIN = 15
        self._config = config
        self._temp = None
        self._humi = None
        self._dht22 = dht.DHT22(Pin(self._PIN))

    @property
    def temp(self) -> float:
        return self._temp

    @temp.setter
    def temp(self, value: float) -> None:
        if isinstance(value, float):
            self._temp = value

    @property
    def humi(self) -> float:
        return self._humi

    @humi.setter
    def humi(self, value: float) -> None:
        if isinstance(value, float):
            self._humi = value

    def measure(self) -> None:
        """Realiza a leitura do sensor."""
        try:
            self._dht22.measure()
            self.temp = self._dht22.temperature() + self._config.TEMP_SETTING
            self.humi = self._dht22.humidity() + self._config.HUMI_SETTING
        except Exception as e:
            print(f'Falha ao ler sensor: {e}')

    def get(self) -> dict:
        """Retorna um objeto com os últimos valores lidos e o id do dispositivo."""
        return {'id_device': self._config.MQTT_CLIENT,'temp_value': round(self.temp, 2), 'humi_value': round(self.humi, 2)}

    def get_json(self) -> str:
        """Retorna uma string em formato json com os últimos valores lidos e o id do dispositivo."""
        return json.dumps(
            {'id_device': self._config.MQTT_CLIENT,'temp_value': round(self.temp, 2), 'humi_value': round(self.humi, 2)}
        )

    def __str__(self) -> str:
        """Representa o objeto como texto."""
        return f'Sensor(pin={self._PIN}, temp={self.temp:.2f} \xDFC, humi={self.humi:.2f} %)'


class Buzzer:
    """Implementa a classe de Buzzer."""
    def __init__(self) -> None:
        self._PIN = 4
        self._PIN_LED = 2
        self._buzzer = Pin(self._PIN, Pin.OUT)
        self._led = Pin(self._PIN_LED, Pin.OUT)
        self._status = False

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, value: bool) -> None:
        if isinstance(value, bool):
            self._status = value

    def on(self) -> None:
        """Liga o buzzer."""
        self._buzzer.on()
        self._led.on()
        self.status = True

    def off(self) -> None:
        """Desliga o buzzer."""
        self._buzzer.off()
        self._led.off()
        self.status = False

    def __str__(self) -> str:
        """Representa o objeto como texto."""
        return (
            f'Buzzer(pin={self._PIN}, status={"ON" if self.status else "OFF"})'
        )


class Wifi:
    """Implementa a classe de WiFi."""
    def __init__(self, config: Config, lcd: Lcd) -> None:
        self._mac = None
        self._client = network.WLAN(network.STA_IF)
        self._client.active(True)
        self._config = config
        self._lcd = lcd
        self.mac = self._mac_to_str(self._client.config('mac'))
        if self._config.MAC_ADDRESS != self.mac:
            self._config.update({'MAC_ADDRESS': self.mac})

    @property
    def mac(self) -> str:
        return self._mac

    @mac.setter
    def mac(self, value: str) -> None:
        if isinstance(value, str):
            self._mac = value

    def _mac_to_str(self, mac) -> str:
        """Converte MAC hexadecimal para texto."""
        return ''.join([f'{b:02X}' for b in mac]).upper()

    def isconnected(self) -> bool:
        """Verifica de existe conexão WiFi."""
        return self._client.isconnected()

    def connect(self) -> None:
        """Realiza a conexão WiFi."""
        self._lcd.clear()
        self._lcd.write(f'MAC:\n{self.mac}')
        sleep(2)
        self._client.connect(
            self._config.WIFI_SSID, self._config.WIFI_PASSWORD
        )
        while not self.isconnected():
            print('Conectando . . .')
            self._lcd.clear()
            self._lcd.write('Conectando . . .')
            sleep(0.1)
        print('WiFi Conectado!')
        print(self._client.ifconfig())
        self._lcd.clear()
        self._lcd.write('WiFi Conectado!')
        sleep(2)

    def __str__(self) -> str:
        """Representa o objeto como texto."""
        return self._client.ifconfig()


class Mqtt:
    """Implementa a classe de MQTT."""
    def __init__(self, config: Config, lcd: Lcd) -> None:
        self._config = config
        self._lcd = lcd

    def _callback(self, topic, message):
        """Recebe e trata a mensagem recebida."""
        if topic == self._config.MQTT_CONFIG_TOPIC.encode():
            print('ESP recebeu uma mensagem!')
            data = json.loads(message.decode())
            print(f'mensagem:{data}')
            if 'MQTT_CLIENT' in data.keys():
                sensor = data.pop('MQTT_CLIENT')
                if sensor == self._config.MQTT_CLIENT:
                    self._config.update(data)
                    print('Configuração atualizada!')
                    machine.reset()
                else:
                    print('A mensagem não é para esse dispositivo')
            else:
                print('Sem informação do dispositivo de destino!"')

    def connect(self) -> None:
        """Realiza a conexão com o broker."""
        print('Conectando ao MQTT broker ...', end='')
        try:
            self._client = MQTTClient(
                self._config.MQTT_CLIENT, self._config.MQTT_BROKER
            )
            self._client.set_callback(self._callback)
            self._client.connect()
            print('Conectado.')
            self._client.subscribe(self._config.MQTT_CONFIG_TOPIC)
        except Exception as e:
            print(f'Falha na conexão com o broker: {e}')
            print(f'Reiniciando . . .')
            sleep(2)
            machine.reset()
        return self._client

    def publish(self, topic, data) -> None:
        """Publica uma mensagem ao broker."""
        print('\nPublicando uma mensagem...')
        self._client.publish(topic, data)
        print(data)

    def publish_data(self, data) -> None:
        """Publica um objeto ao broker."""
        self.publish(self._config.MQTT_SENSOR_TOPIC, data)

    def check_msg(self):
        """Verifica se alguma mensagem foi recebida."""
        self._client.check_msg()

    def __str__(self) -> str:
        """Representa o objeto como texto."""
        return f'Mqtt(pub_topic={self._config.MQTT_SENSOR_TOPIC},sub_topic={self._config.MQTT_CONFIG_TOPIC})'


def run():
    """Cria os objetos necessários e realiza a rotina de medição."""
    config = Config()
    lcd = Lcd()
    sensor = Sensor(config=config)
    buzzer = Buzzer()
    wifi = Wifi(config=config, lcd=lcd)
    mqtt_client = Mqtt(config=config, lcd=lcd)
    wifi.connect()
    mqtt_client.connect()

    print('#### CONFIGURACAO ATUAL ####')
    print(f'# TEMP_LIMIT_LOWER = {config.TEMP_LIMIT_LOWER:5.2f} #')
    print(f'# TEMP_LIMIT_UPPER = {config.TEMP_LIMIT_UPPER:5.2f} #')
    print(f'# TEMP_SETTING     = {config.TEMP_SETTING:5.2f} #')
    print(f'# HUMI_LIMIT_LOWER = {config.HUMI_LIMIT_LOWER:5.2f} #')
    print(f'# HUMI_LIMIT_UPPER = {config.HUMI_LIMIT_UPPER:5.2f} #')
    print(f'# HUMI_SETTING     = {config.HUMI_SETTING:5.2f} #')
    print('####################################################')
    
    last_read = time() - (config.DELAY_MEASURE + 1)
    last_buzzer = time() - (config.DELAY_BUZZER_OFF + 1)
    last_buzzer_on = time() - (config.DELAY_BUZZER_ON + 1)
    buzzer_on = False

    while True:
        try:
            sleep(2)
            now = time()
            if now - last_read >= config.DELAY_MEASURE:
                sensor.measure()
                data = sensor.get()
                temp = data['temp_value']
                humi = data['humi_value']
                print(f'Temp: {temp} °C\nHumi: {humi} %')
                mqtt_client.publish_data(sensor.get_json())
                lcd.write_data(data=data)
                last_read = time()
            if (
                temp < config.TEMP_LIMIT_LOWER
                or temp > config.TEMP_LIMIT_UPPER
                or humi < config.HUMI_LIMIT_LOWER
                or humi > config.HUMI_LIMIT_UPPER
            ):
                if not buzzer_on and now - last_buzzer >= config.DELAY_BUZZER_OFF:
                    buzzer.on()
                    last_buzzer_on = time()
                    buzzer_on = True
                    print('buzzer ligado')
            if buzzer_on and now - last_buzzer_on >= config.DELAY_BUZZER_ON:
                buzzer.off()
                buzzer_on = False
                print('buzzer desligado')
                last_buzzer = time()
            sleep(1)
            mqtt_client.check_msg()
            print('. ', end='')
        except Exception as e:
            print(f'ERRO: {e}')


if __name__ == '__main__':
    
    run()
