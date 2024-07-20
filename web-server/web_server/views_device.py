from flask import (
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for,
    jsonify,
)
from sqlalchemy import func
from app import app, db, mqtt, MQTT_CONFIG_TOPIC, MQTT_SENSOR_TOPIC
from models import TbDevices, TbRegisters, TbHistory
from helpers import (
    FormDevice,
)
from pytz import timezone
from datetime import datetime
import json
from dataclasses import dataclass


@dataclass
class Device:
    id_device: str
    temp_limit_upper: str
    temp_limit_lower: str
    humi_limit_upper: str
    humi_limit_lower: str
    temp_value: str
    humi_value: str
    last_update: str


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic, payload=json.loads(message.payload.decode())
    )
    print(json.dumps(data))

    if data['topic'] == MQTT_SENSOR_TOPIC:
        new_register = TbRegisters(
            id_device=data['payload']['id_device'],
            temp_value=data['payload']['temp_value'],
            humi_value=data['payload']['humi_value'],
        )
        with app.app_context():
            db.session.add(new_register)
            db.session.commit()


@app.route('/')
def index():
    devices = db.session.query(TbDevices).distinct(TbDevices.id_device).all()
    data = []

    for device in devices:
        last_register = (
            db.session.query(TbRegisters)
            .join(
                TbDevices,
                TbDevices.id_device == TbRegisters.id_device,
            )
            .filter(TbDevices.id_device == device.id_device)
            .order_by(TbRegisters.created_at.desc())
            .first()
        )
        print(last_register)
        if last_register:
            data.append(
                Device(
                    device.id_device,
                    device.temp_limit_upper,
                    device.temp_limit_lower,
                    device.humi_limit_upper,
                    device.humi_limit_lower,
                    last_register.temp_value,
                    last_register.humi_value,
                    last_register.created_at.astimezone(
                        timezone('America/Manaus')
                    ).strftime('%d/%m/%Y %H:%M'),
                )
            )

        else:
            data.append(
                Device(
                    device.id_device,
                    device.temp_limit_upper,
                    device.temp_limit_lower,
                    device.humi_limit_upper,
                    device.humi_limit_lower,
                    'N/A',
                    'N/A',
                    'N/A',
                )
            )
            print(data)
    return render_template('dashboard.html', title='Painel', data=data)


@app.route('/devices')
def devices():
    lista = TbDevices.query.order_by(TbDevices.id_device)
    print(lista)
    return render_template('devices.html', title='Dispositivos', devices=lista)


@app.route('/registers')
def registers():
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect(url_for('login', next=url_for('registers')))
    lista = TbRegisters.query.order_by(TbRegisters.id)
    print(lista)
    return render_template(
        'registers.html', title='Registros', registers=lista
    )


@app.route('/history')
def history():
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect(url_for('login', next=url_for('history')))
    lista = TbHistory.query.order_by(TbHistory.id)
    print(lista)
    return render_template('history.html', title='Histórico', registers=lista)


@app.route('/new')
def new():
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect(url_for('login', next=url_for('new')))
    form = FormDevice()
    return render_template('new.html', title='Novo Dispositivo', form=form)


@app.route(
    '/create',
    methods=[
        'POST',
    ],
)
def create():
    form = FormDevice(request.form)

    if not form.validate_on_submit():
        flash('Parâmetros inválidos!')
        return redirect(url_for('new'))

    id_device = form.id_device.data
    temp_limit_upper = form.temp_limit_upper.data
    temp_limit_lower = form.temp_limit_lower.data
    temp_limit_setting = form.temp_limit_setting.data
    humi_limit_upper = form.humi_limit_upper.data
    humi_limit_lower = form.humi_limit_lower.data
    humi_limit_setting = form.humi_limit_setting.data

    device = TbDevices.query.filter_by(id_device=id_device).first()

    if device:
        flash('Dispositivo já existe!')
        return redirect(url_for('devices'))

    new_device = TbDevices(
        id_device=id_device,
        temp_limit_upper=temp_limit_upper,
        temp_limit_lower=temp_limit_lower,
        temp_limit_setting=temp_limit_setting,
        humi_limit_upper=humi_limit_upper,
        humi_limit_lower=humi_limit_lower,
        humi_limit_setting=humi_limit_setting,
    )
    new_history = TbHistory(
        id_device=id_device,
        action='CRIADO',
        temp_limit_upper=temp_limit_upper,
        temp_limit_lower=temp_limit_lower,
        temp_limit_setting=temp_limit_setting,
        humi_limit_upper=humi_limit_upper,
        humi_limit_lower=humi_limit_lower,
        humi_limit_setting=humi_limit_setting,
    )

    db.session.add(new_device)
    db.session.add(new_history)
    db.session.commit()

    device_message = json.dumps(
        {
            'MQTT_CLIENT': id_device,
            'TEMP_LIMIT_UPPER': temp_limit_upper,
            'TEMP_LIMIT_LOWER': temp_limit_lower,
            'TEMP_SETTING': temp_limit_setting,
            'HUMI_LIMIT_UPPER': humi_limit_upper,
            'HUMI_LIMIT_LOWER': humi_limit_lower,
            'HUMI_SETTING': humi_limit_setting,
        }
    )
    mqtt.publish(MQTT_CONFIG_TOPIC, device_message)
    print(f'Mensagem enviada: {device_message}')

    flash(f"Dispositivo '{form.id_device.data}' criado com sucesso!")
    return redirect(url_for('devices'))


@app.route('/edit/<id_device>')
def edit(id_device):
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect(
            url_for('login', next=url_for('edit', id_device=id_device))
        )
    device = TbDevices.query.filter_by(id_device=id_device).first()
    form = FormDevice()
    form.id_device.data = device.id_device
    form.temp_limit_upper.data = device.temp_limit_upper
    form.temp_limit_lower.data = device.temp_limit_lower
    form.temp_limit_setting.data = device.temp_limit_setting
    form.humi_limit_upper.data = device.humi_limit_upper
    form.humi_limit_lower.data = device.humi_limit_lower
    form.humi_limit_setting.data = device.humi_limit_setting
    return render_template(
        'edit.html',
        title='Editar Dispositivo',
        id_device=id_device,
        form=form,
    )


@app.route(
    '/update',
    methods=[
        'POST',
    ],
)
def update():
    form = FormDevice(request.form)
    print(repr(form))
    print(repr(form.id_device.data))
    if form.validate_on_submit():
        device = TbDevices.query.filter_by(
            id_device=request.form['id_device']
        ).first()
        device.id_device = form.id_device.data
        device.temp_limit_upper = form.temp_limit_upper.data
        device.temp_limit_lower = form.temp_limit_lower.data
        device.temp_limit_setting = form.temp_limit_setting.data
        device.humi_limit_upper = form.humi_limit_upper.data
        device.humi_limit_lower = form.humi_limit_lower.data
        device.humi_limit_setting = form.humi_limit_setting.data
        print(form.id_device.data)

        new_history = TbHistory(
            id_device=device.id_device,
            action='MODIFICADO',
            temp_limit_upper=device.temp_limit_upper,
            temp_limit_lower=device.temp_limit_lower,
            temp_limit_setting=device.temp_limit_setting,
            humi_limit_upper=device.humi_limit_upper,
            humi_limit_lower=device.humi_limit_lower,
            humi_limit_setting=device.humi_limit_setting,
        )

        db.session.add(new_history)
        db.session.add(device)
        db.session.commit()

        device_message = json.dumps(
            {
                'MQTT_CLIENT': device.id_device,
                'TEMP_LIMIT_UPPER': device.temp_limit_upper,
                'TEMP_LIMIT_LOWER': device.temp_limit_lower,
                'TEMP_SETTING': device.temp_limit_setting,
                'HUMI_LIMIT_UPPER': device.humi_limit_upper,
                'HUMI_LIMIT_LOWER': device.humi_limit_lower,
                'HUMI_SETTING': device.humi_limit_setting,
            }
        )

        mqtt.publish(MQTT_CONFIG_TOPIC, device_message)
        flash(
            f'Dispositivo \'{request.form["id_device"]}\' modificado com sucesso!'
        )
    else:
        flash('Parâmetros inválidos!')
    return redirect(url_for('devices'))


@app.route('/delete/<id_device>')
def delete(id_device):
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect(url_for('login'))

    device = TbDevices.query.filter_by(id_device=id_device).first()

    new_history = TbHistory(
        id_device=device.id_device,
        action='DELETADO',
        temp_limit_upper=device.temp_limit_upper,
        temp_limit_lower=device.temp_limit_lower,
        temp_limit_setting=device.temp_limit_setting,
        humi_limit_upper=device.humi_limit_upper,
        humi_limit_lower=device.humi_limit_lower,
        humi_limit_setting=device.humi_limit_setting,
    )
    db.session.add(new_history)
    db.session.commit()

    TbDevices.query.filter_by(id_device=id_device).delete()
    db.session.commit()
    flash(f"Dispositivo '{id_device}' deletado com sucesso!")

    return redirect(url_for('devices'))
