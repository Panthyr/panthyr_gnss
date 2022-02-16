#! /usr/bin/python3
# -*- coding: utf-8 -*-
import logging
from time import sleep

import serial  # type: ignore
from gnss_messages import GGAMessage
from gnss_messages import RMCMessage

GPS_BAUDRATE: int = 9600
GPS_SERIALPORT: str = '/dev/ttyO4'


class Gnss():

    def __init__(self,
                 port: str = GPS_SERIALPORT,
                 baudrate: int = GPS_BAUDRATE) -> None:
        """Collect time, geoposition and others from GNSS GGA and RMC string.

        Args:
            port (str, optional): serial port name. Defaults to GPS_SERIALPORT.
            baudrate (int, optional): data baudrate. Defaults to GPS_BAUDRATE.
        """
        self.log: logging.Logger = logging.getLogger(
            f'__main__.{__name__}')
        self._create_port(port, baudrate)

    def _create_port(self, port: str,
                     baudrate: int) -> None:
        """Create and flush the serial port.

        Uses a timeout of 0.5 seconds, otherwise default parameters.

        Args:
            port (str): serial port name.
            baudrate (int): data baudrate.
        """
        try:
            self.serport: serial.Serial = serial.Serial(
                port=port, baudrate=baudrate, timeout=0.5)
            self.serport.close()  # make sure port is closed
            self.serport.open()
            self.serport.flushInput(
            )  # clear the input buffer

        except Exception as e:  # TODO: replace by correct exception from serial class
            self.log.error(
                f'Error while setting up GNSS port (ARE YOU ROOT?): {e}'
            )
            raise

    def get_nmea(self, timeout: int = 45) -> bool:
        """Try to parse GGA and RMC from serial port

        Reads from serial port and tries to extract GGA and RMC messages.
        Creates new data objects, then extracts data from the serial rx buffer.
            Wait for a new message to come in (starts with '$').
            When a full message (start with '$' and ending with '/r/n') has been received,
                check if it is a valid GGA or RMC msg. If so, extract data. Throw away msg if not.
            Check if both GGA and RMC data have been received. Return True if so.
        Continue until timeout has expired.

        Args:
            timeout (int, optional): timeout for correct messages to arrive (s). Defaults to 45.

        Returns:
            bool: True if valid GGA and RMC messages have been received and parsed, False if not.
        """

        timeout *= 4  # we'll check every 250ms
        self._prepare_data_objs()

        while timeout:
            if self._read_serial_buffer(
            ):  # new data has come in
                self._clean_up_buffer()

            timeout -= 1
            sleep(0.25)

        return False

    def _prepare_data_objs(self):
        """Create new objects/variables to hold data.

        Create new objects for GGA and RMC messages and a buffer for incoming data.
        """
        self.gga: GGAMessage = GGAMessage()
        self.rmc: RMCMessage = RMCMessage()
        self._incoming_data: str = ''  # incoming chars from uart buffer

    def _read_serial_buffer(self) -> int:
        """Read data from serial port Rx buffer.

        Move all characters from the serial port Rx buffer to our own buffer.

        Returns:
            int: number of characters copied from uart to incoming buffer.
        """
        read: int = 0
        while self.serport.inWaiting() > 0:
            self._incoming_data += self.serport.read(
                1).decode()  # Read one char from the buffer
            read += 1
        return read

    def _clean_up_buffer(self):
        """ Tidy up incoming data buffer.

        A msg starts with '$'. All data received before that is from a lost msg. Remove that data.
        A msg ends with '\r\n'. If a full message is received,
            move that data to the _new_full_message buffer.
        """
        msg_start = self._incoming_data.find('$')

        self._incoming_data = self._incoming_data[
            msg_start:]


test_string = (
    'garbage\r\n$GPGGA,133933.000,5114.16147,N,00255.70634,E,1,09,1.0,011.91,M,47.1,M'
    ',,*66\r\n$GPRMC,204804.000,V,4520.254,N,07554.206,W,0.0,0.0,200608,0.0,W*7E\r\ngarbage'
)
