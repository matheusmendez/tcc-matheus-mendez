import os
from app import app
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    SubmitField,
    PasswordField,
    IntegerField,
    validators,
)


class FormDevice(FlaskForm):
    id_device = StringField(
        'ID_Dispositivo',
        [validators.DataRequired(), validators.Length(min=1, max=30)],
    )
    temp_limit_upper = FloatField(
        'Limite_Superior_Temperatura',
        [validators.NumberRange(min=-100, max=100)],
    )
    temp_limit_lower = FloatField(
        'Limite_Inferior_Temperatura',
        [validators.NumberRange(min=-100, max=100)],
    )
    temp_limit_setting = FloatField(
        'Ajuste_Temperatura', [validators.NumberRange(min=-100, max=100)]
    )
    humi_limit_upper = FloatField(
        'Limite_Superior_Umidade', [validators.NumberRange(min=-100, max=100)]
    )
    humi_limit_lower = FloatField(
        'Limite_Inferior_Umidade', [validators.NumberRange(min=-100, max=100)]
    )
    humi_limit_setting = FloatField(
        'Ajuste_Umidade', [validators.NumberRange(min=-100, max=100)]
    )

    save = SubmitField('Salvar')


class FormUser(FlaskForm):
    userid = StringField(
        'Usuário', [validators.DataRequired(), validators.Length(min=1, max=8)]
    )
    password = PasswordField(
        'Senha',
        [validators.DataRequired(), validators.Length(min=1, max=100)],
    )
    login = SubmitField('Login')
