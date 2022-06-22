#! /usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'Dieter Vansteenwegen'
__email__ = 'dieter.vansteenwegen@vliz.be'
__project__ = 'Panthyr'
__project_link__ = 'https://waterhypernet.org/equipment/'

from . import p_gnss
from panthyr_gpio.p_gpio import pGPIO
from time import sleep

PORT: str = '/dev/ttyO4'
BAUDRATE: int = 9600
LOOP_TIME: int = 2
NMEA_TIMEOUT: int = 5
GPIO_PIN = (0, 8)

WELCOME_MSG = (
    'This will check for incoming data from the GNSS. '
    'If the receiver does not have clear sight to the sky, don\'t expect a position fix. \r\n'
    'Getting a fix might take up to a minute, even with a clear view on the sky.\r\n\r\n'
    f'Assumes: \r\n- receiver is connected to port {PORT}\r\n- set to {BAUDRATE} baud\r\n- powered from  '
    f'chip {GPIO_PIN[0]}, offset {GPIO_PIN[1]}.\r\n\r\n'
    f'Loop time set to {LOOP_TIME} seconds, timeout set to {NMEA_TIMEOUT} seconds.\r\n'
    'Hit CTRL+C to exit...'
)


def test_gnss():
    counter: int = 1
    print(WELCOME_MSG)
    gpio = pGPIO(GPIO_PIN[0], GPIO_PIN[1], 'out', 1)
    try:
        while True:
            rtn = p_gnss.get_nmea(
                timeout=NMEA_TIMEOUT,
                port=PORT,
            )

            print(
                f'Loop {counter}, message: {rtn or "No data received"}',
            )

            counter += 1
            sleep(LOOP_TIME)
    except KeyboardInterrupt:
        gpio.off()
        print('CTRL+C detected, exiting...')


if __name__ == '__main__':
    test_gnss()
