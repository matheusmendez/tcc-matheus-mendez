"""Provê uma classe de LCD I2C baseada na classe LcdApi."""

# Módulos padrão do MicroPython
import gc
import time
from machine import I2C

# Módulo importado de outra fonte - MIT license
# https://github.com/dhylands/python_lcd/blob/master/lcd/lcd_api.py
from lcd_api import LcdApi

# Definição dos pinos
MASK_RS = 0x01       # P0
MASK_RW = 0x02       # P1
MASK_E = 0x04       # P2

SHIFT_BACKLIGHT = 3  # P3
SHIFT_DATA = 4  # P4-P7


class LcdI2c(LcdApi):
    """Implementa uma classe de LCD ligado através de I2C."""
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.i2c.writeto(self.i2c_addr, bytes([0]))
        time.sleep_ms(20) 
        self.hal_write_init(self.LCD_FUNCTION_RESET)
        time.sleep_ms(5)
        self.hal_write_init(self.LCD_FUNCTION_RESET)
        time.sleep_ms(1)
        self.hal_write_init(self.LCD_FUNCTION_RESET)
        time.sleep_ms(1)
        self.hal_write_init(self.LCD_FUNCTION)
        time.sleep_ms(1)
        LcdApi.__init__(self, num_lines, num_columns)
        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)
        gc.collect()

    def hal_write_init(self, nibble):
        """Escreve comando para inicalização do LCD."""
        byte = ((nibble >> 4) & 0x0F) << SHIFT_DATA
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        gc.collect()

    def hal_backlight_on(self):
        """Liga o backlight."""
        self.i2c.writeto(self.i2c_addr, bytes([1 << SHIFT_BACKLIGHT]))
        gc.collect()

    def hal_backlight_off(self):
        """Desliga o bakclight."""
        self.i2c.writeto(self.i2c_addr, bytes([0]))
        gc.collect()

    def hal_write_command(self, cmd):
        """Escreve um comando ao LCD."""
        byte = (self.backlight << SHIFT_BACKLIGHT) | (
            ((cmd >> 4) & 0x0F) << SHIFT_DATA
        )
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = (self.backlight << SHIFT_BACKLIGHT) | (
            (cmd & 0x0F) << SHIFT_DATA
        )
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        if cmd <= 3:
            time.sleep_ms(5)
        gc.collect()

    def hal_write_data(self, data):
        """Escreve um dado ao LCD."""
        byte = (
            MASK_RS
            | (self.backlight << SHIFT_BACKLIGHT)
            | (((data >> 4) & 0x0F) << SHIFT_DATA)
        )
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = (
            MASK_RS
            | (self.backlight << SHIFT_BACKLIGHT)
            | ((data & 0x0F) << SHIFT_DATA)
        )
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        gc.collect()
