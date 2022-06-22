#! /usr/bin/python
# -*- coding: utf-8 -*-
"""Collect time, geoposition and others from GNSS GGA and RMC string.

Ver 2.0 19mar2018

Project: Hypermaq
Dieter Vansteenwegen, VLIZ Belgium
Copyright?

Example GGA string: $GPGGA,133933.000,5114.16147,N,00255.70634,E,1,09,1.0,011.91,M,47.1,M,,*66
GGA message fields (comma separated):
Field 	Meaning
0 	Message ID $GPGGA
1 	UTC of position fix
2 	Latitude in degrees minutes.m
3 	Direction of latitude: N: North S: South
4 	Longitude in degrees minutes.m
5 	Direction of longitude: E: East W: West
6 	GPS Quality indicator:
        0: Fix not valid
        1: GPS fix
        2: Differential GPS fix, OmniSTAR VBS
        4: Real-Time Kinematic, fixed integers
        5: Real-Time Kinematic, float integers, OmniSTAR XP/HP or Location RTK
7 	Number of SVs in use, range from 00 through to 24+
8 	HDOP
9 	Orthometric height (MSL reference)
10 	M: unit of measure for orthometric height is meters
11 	Geoid separation
12 	M: geoid separation measured in meters
13 	Age of differential GPS data record, Type 1 or Type 9. Null field when DGPS is not used.
14 	Reference station ID, range 0000-4095. A null field when any reference station ID is selected
    and no corrections are received1.
15  The checksum data

Example RMC (Recommended minimum) string:
    $GPRMC,204804.000,V,4520.254,N,07554.206,W,0.0,0.0,200608,0.0,W*7E
RMC message fields (comma separated):
Field 	Meaning
0  Message ID $GPRMC
1  UTC of position fix
2  Data status (A= Data valid, V=navigation receiver warning)
3  Latitude of fix
4  N or S
5  Longitude of fix
6  E or W
7  Speed over ground in knots
8  Track made good in degrees true
9  UTC date
10  Magnetic variation degrees (Easterly var. subtracts from true course)
11  E or W
(12) NMEA 2.3 and later: FAA mode indicator, might or might not be in the message depending
    on gps configuration. Code should work with either.
12/13  Checksum
"""
import datetime
import logging
import time  # used for delay function and timestamp

import serial

GPS_BAUDRATE = 9600
GPS_PORT = '/dev/ttyO4'

parsed = {}

__all__ = ['get_nmea']

log = logging.getLogger(__name__)


def setup_port(port: str) -> serial.Serial:
    """Setup of serial port."""

    serport = serial.Serial(
        port=port,
        baudrate=GPS_BAUDRATE,
        timeout=0.5,
    )
    serport.close()  # make sure port is closed
    serport.open()
    return serport


def get_nmea(port: str = GPS_PORT, timeout=45):
    """Parses data from GNSS receiver looking for the NMEA strings that we are interested in.

    CRC and 'Data status' (RMC) or 'GPS Quality' (GGA) field is checked before continuing.
    Returns a dict with the following items:
    [utc]: Datetime object
    [lat]: type: real. Expressed in decimal degrees. Positive is North, negative is South.
    [lon]: type: real. Expressed in decimal degrees. Positive is East, negative is West.
    [qual]: GPS quality, (0: invalid, 1: GPS fix, 2: Diff GPS fix, 3: OmniSTAR VBS,
                            4: RTK fix, 5: RTK Float)
    [height]: type real. Expressed in meters above MSL
    [mag_var]: type real. Local magnetic variation in degrees, positive  means W,
                            add to true course
    Timeout is the maximum amount of seconds waiting for a valid combination of GGA and RMC
    """
    serport = setup_port(port)
    uart_buffer_str = ''  # will use this a buffer for the incoming data
    valid_gga = []  # list that will hold the valid GGA data
    valid_rmc = []  # list that will hold the valid RMC data
    timeout = timeout * 2  # using 0.5s sleep time
    global parsed

    serport.close(
    )  # reset port, got random 'device reports readiness to read but returned no data
    # (device disconnected or multiple access on port?)' errors
    serport.open()
    serport.flushInput()  # clear the input buffer

    while timeout:
        while serport.inWaiting(
        ) > 0:  # Loop as long as there are chars in serial port buffer
            read = serport.read(1)
            try:
                uart_buffer_str += read.decode(
                )  # Read from the buffer, one character at a time
            except UnicodeDecodeError:
                log.debug(
                    f'UnicodeDecodeError: Could not decode incoming byte [{read}], current string: {uart_buffer_str}',
                )
                uart_buffer_str = ''
            if uart_buffer_str.endswith(
                    '\r\n', ):  # If a newline is found
                full_string = uart_buffer_str.strip(
                )  # Put message without newline chars in variable
                uart_buffer_str = ''  # Clear the buffer to receive a new line

                if full_string.startswith(
                        '$G',
                ) and full_string[
                        3:7
                ] == 'GGA,' and __check_checksum(
                            full_string,
                ) and __check_gps_quality(
                            full_string, ) > 0:
                    valid_gga = full_string[:-3].split(
                        ',',
                    )  # store the string as a valid gga message

                if full_string.startswith(
                        '$G',
                ) and full_string[
                        3:
                        7
                ] == 'RMC,' and valid_gga != '' and __check_checksum(
                            full_string, ):
                    valid_rmc = full_string[:-3].split(
                        ',',
                    )  # store the string as a valid rmc message

                if valid_gga and valid_rmc:  # we have valid gga and rmc messages so parse the data
                    dt_result = __parse_datetime(
                        valid_gga,
                        valid_rmc,
                    )
                    ch_result = __parse_coordinates_height(
                        valid_gga,
                        valid_rmc,
                    )
                    qu_result = __parse_qual_mag_var(
                        valid_rmc,
                        valid_gga,
                    )
                    if dt_result and ch_result and qu_result:
                        return parsed
        time.sleep(0.5)
        timeout -= 1

    return False


def __check_checksum(source):
    # sourcery skip: assign-if-exp, boolean-if-exp-identity, remove-unnecessary-cast
    """NMEA string checksum.

    Last two characters of a NMEA string are a CRC check. XOR each character
    (binary ASCII representation) between $ and *. Convert to base 16 to get the CRC.
    """
    str_stripped_message = source[
        1:
        -3
    ]  # only part between $ and before *CRC are used
    crc = 0
    for character in str_stripped_message:
        crc = crc ^ ord(
            character,
        )  # xor each character with the previous CRC solution
    if str(hex(crc)[2:]) == source[-2:].lower(
    ):  # check if our crc corresponds with the received one
        return (True)
    else:
        return (False)


def __check_gps_quality(gga_message):
    """GGA position validity check.

    6th field of GGA message is the GPS Quality indicator:
            0: Fix not valid
            1: GPS fix
            2: Differential GPS fix
            4: Real-Time Kinematic, fixed integers
            5: Real-Time Kinematic, float integers
    Returns 0 if fix is invalid/exception occurs, or returns the indicator if valid
    """
    try:
        gps_quality = int(
            gga_message.split(',')[6],
        )  # split the message at commas, the sixt parameter is the gps quality
        return gps_quality if 0 <= gps_quality < 6 else 0
    except Exception:
        return 0


def __parse_datetime(gga_list, rmc_list):
    """Gets the UTC time from the gga_list and date from rmc_list.

    Results are added to parsed["utc"].
    Returns true if succeeded, false if fails.
    """
    global parsed

    if not gga_list or not rmc_list:
        return False

    try:  # gga message contains time in format HHMMSS.ms
        index = gga_list[1].index(
            '.', )  # check the index of '.'
        timestring = (
            gga_list[1]
        )[:index]  # and use that to keep only HHMMSS
    except ValueError:  # index method raises ValueError if no index found
        timestring = gga_list[1]

    datetimestring = timestring + rmc_list[
        9
    ]  # add the date to the time
    parsed['utc'] = datetime.datetime.strptime(
        datetimestring,
        '%H%M%S%d%m%y',
    )

    return True


def __parse_coordinates_height(gga_list, rmc_list):
    """Gets the coordinates and height from gga_list and rmc_list.

    Coordinates received in the GGA string are in degrees minutes.m format (always positive)
    Returned coordinates are in format decimal degrees
    lat: Positive is North, negative is South
    lon: Positive is East, negative is West
    Height is in meters.
    Results are stored in parsed[lat], parsed[lon] and parsed[height].
    """
    global parsed

    lat_degrees_minutes = float(gga_list[2])
    lat_degrees = (lat_degrees_minutes // 100) + (
        (lat_degrees_minutes % 100) / 60
    )  # convert from degrees minutes.m to decimal degrees

    parsed['lat'] = lat_degrees if gga_list[
        3
    ] == 'N' else -lat_degrees
    lon_degrees_minutes = float(gga_list[4])
    lon_degrees = (lon_degrees_minutes // 100) + (
        (lon_degrees_minutes % 100) / 60
    )  # convert from degrees minutes.m to decimal degrees

    parsed['lon'] = lon_degrees if gga_list[
        5
    ] == 'E' else -lon_degrees
    parsed['height'] = float(gga_list[9])

    return True


def __parse_qual_mag_var(rmc_list, gga_list):
    """Stores the local magnetic variation in parsed["mag_var"] as an integer.
        Positive is East, negative is West
    """
    global parsed

    if rmc_list[11] == '':
        parsed['mag_var'] = None
    elif rmc_list[11] == 'E':
        parsed['mag_var'] = float(rmc_list[10])
    elif rmc_list[11] == 'S':
        parsed['mag_var'] = -float(rmc_list[10])

    parsed['qual'] = int(gga_list[6])
    return True
