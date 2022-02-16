# -*- coding: utf-8 -*-
# #! /usr/bin/python3
# # -*- coding: utf-8 -*-
# import datetime
# import logging
# import time
# from typing import Dict
# # from typing import Union
# import serial  # type: ignore
# GPS_BAUDRATE: int = 9600
# GPS_SERIALPORT: str = '/dev/ttyO4'
# class gnss():
#         """Parses data from GNSS receiver looking for the NMEA strings that we are interested in.
#         CRC and "Data status" (RMC) or "GPS Quality" (GGA) field is checked before continuing.
#         Returns a dict with the following items:
#         [utc]: Datetime object
#         [lat]: type: real. Expressed in decimal degrees. Positive is North, negative is South.
#         [lon]: type: real. Expressed in decimal degrees. Positive is East, negative is West.
#         [qual]: GPS quality, (0: invalid, 1: GPS fix, 2: Diff GPS fix, 3: OmniSTAR VBS, 4: RTK fix, 5: RTK Float)
#         [height]: type real. Expressed in meters above MSL
#         [mag_var]: type real. Local magnetic variation in degrees, positive  means W, add to true course
#         Timeout is the maximum amount of seconds waiting for a valid combination of GGA and RMC
#         """
#     def get_nmea(self, timeout: int = 45):
#         """_summary_
#         _extended_summary_
#         Args:
#             timeout (int, optional): timeout for correct messages to come (s). Defaults to 45.
#         Returns:
#             _type_: _description_
#         """
#         # self.parsed: Dict = {
#         # }  # will get all the data when parsed from the nmea messages
#         # print(
#         #     f'This should be empty, check!: {self.parsed}')
#         # self.uart_buffer: str = ''  # will use this a buffer for the incoming data
#         # self.valid_gga: list = [
#         # ]  # list that will hold the valid GGA data
#         # self.valid_rmc: list = [
#         # ]  # list that will hold the valid RMC data
#         # timeout *= 2  # using 0.5s sleep time
#         # self._prepare_port()
#         # while timeout:
#         #     self._read_buffer()
#         #     if full_string := self._extract_line():
#         #         self._check_gga(full_string)
#                 # if (full_string[:7] == '$GPRMC,'
#                 #         and valid_gga != ''
#                 #         and self._check_checksum(
#                 #             full_string)):
#                 #     valid_rmc = full_string[:-3].split(
#                 #         ','
#                 #     )  # store the string as a valid rmc message
#                 # if valid_gga and valid_rmc:  # we have valid gga and rmc messages, so let's parse the data
#                 #     dt_result = self._parse_datetime(
#                 #         valid_gga, valid_rmc)
#                 #     ch_result = self._parse_coordinates_height(
#                 #         valid_gga, valid_rmc)
#                 #     qu_result = self._parse_qual_mag_var(
#                 #         valid_rmc, valid_gga)
#                 #     if dt_result and ch_result and qu_result:
#                 #         return self.parsed
#     def _check_gga(self, full_string: str):
#         """Check if full_string is a valid GGA string.
#         Check the following:
#         1. string prefix
#         2. message checksum
#         3. gps quality
#         If the string is valid, extract the data.
#         Args:
#             full_string (str): string to be checked
#         """
#         if (full_string.startswith('$GPGGA,')
#                 and self._check_checksum(full_string)
#                 and self._check_gps_quality(full_string) > 0
#                 and
#                 self._check_gps_quality(full_string) > 0):
#             self.valid_gga = full_string[:-3].split(
#                 ','
#             )  # store the string as a valid gga message
#             # TODO: extract the data here
#     def _extract_line(self):
#         if self.uart_buffer[-2:] != '\r\n':
#             return None
#         full_string = self.uart_buffer.strip()
#         self.uart_buffer = ''  # Clear the buffer to receive a new line
#         return full_string
#     def _prepare_port(self):
#         """" Port needs reset, otherwise you might get random
#         "device reports readiness to read but returned no data
#         (device disconnected or multiple access on port?)"
#         errors
#         """
#         self.serport.close()
#         self.serport.open()
#         self.serport.flushInput()  # clear the input buffer
#     def _check_checksum(self, source):
#         """NMEA string checksum.
#         Last two characters of a NMEA string are a CRC check. XOR each character (binary ASCII representation) between $ and *. Convert to base 16 to get the CRC.
#         """
#         str_stripped_message = source[
#             1:
#             -3]  # only part between $ and before *CRC are used
#         crc = 0
#         for character in str_stripped_message:
#             crc ^= ord(
#                 character
#             )  # xor each character with the previous CRC solution
#         if str(hex(crc)[2:]) == source[-2:].lower(
#         ):  # check if our crc corresponds with the received one
#             return (True)
#         else:
#             return (False)
#     def _check_gps_quality(self, gga_message):
#         """GGA position validity check.
#         6th field of GGA message is the GPS Quality indicator:
#                 0: Fix not valid
#                 1: GPS fix
#                 2: Differential GPS fix
#                 4: Real-Time Kinematic, fixed integers
#                 5: Real-Time Kinematic, float integers
#         Returns 0 if fix is invalid/exception occurs, or returns the indicator if valid
#         """
#         try:
#             gps_quality = int(
#                 gga_message.split(',')[6]
#             )  # split the message at commas, the sixt parameter is the gps quality
#             return gps_quality if 0 <= int(
#                 gps_quality) < 6 else 0
#         except Exception:
#             return 0
#     def _parse_datetime(self, gga_list, rmc_list):
#         """Gets the UTC time from the gga_list and date from rmc_list.
#         Results are added to self.parsed["utc"].
#         Returns true if succeeded, false if fails.
#         """
#         if not gga_list or not rmc_list:
#             return False
#         try:  # gga message contains time in format HHMMSS.ms
#             index = gga_list[1].index(
#                 '.')  # check the index of "."
#             timestring = (
#                 gga_list[1]
#             )[:index]  # and use that to keep only HHMMSS
#         except ValueError:  # index method raises ValueError if no index found
#             timestring = gga_list[1]
#         datetimestring = timestring + rmc_list[
#             9]  # add the date to the time
#         self.parsed['utc'] = datetime.datetime.strptime(
#             datetimestring, '%H%M%S%d%m%y')
#         return True
#     def _parse_coordinates_height(self, gga_list, rmc_list):
#         """Gets the coordinates and height from gga_list and rmc_list.
#         Coordinates received in the GGA string are in degrees minutes.m format (always positive)
#         Returned coordinates are in format decimal degrees
#         lat: Positive is North, negative is South
#         lon: Positive is East, negative is West
#         Height is in meters.
#         Results are stored in self.parsed[lat], self.parsed[lon] and self.parsed[height].
#         """
#         lat_degrees_minutes = float(gga_list[2])
#         lat_degrees = (lat_degrees_minutes // 100) + (
#             (lat_degrees_minutes % 100) / 60
#         )  # convert from degrees minutes.m to decimal degrees
#         if gga_list[3] == 'N':
#             self.parsed['lat'] = lat_degrees
#         else:
#             self.parsed['lat'] = -lat_degrees
#         lon_degrees_minutes = float(gga_list[4])
#         lon_degrees = (lon_degrees_minutes // 100) + (
#             (lon_degrees_minutes % 100) / 60
#         )  # convert from degrees minutes.m to decimal degrees
#         if gga_list[5] == 'E':
#             self.parsed['lon'] = lon_degrees
#         else:
#             self.parsed['lon'] = -lon_degrees
#         self.parsed['height'] = float(gga_list[9])
#         return True
#     def _parse_qual_mag_var(self, rmc_list, gga_list):
#         """Stores the local magnetic variation in self.parsed["mag_var"] as an integer. Positive is East, negative is West"""
#         if rmc_list[
#                 10] == 0:  # there's no mag variation, so set to 0
#             self.parsed['mag_var'] = 0
#         elif rmc_list[11] == 'E':
#             self.parsed['mag_var'] = float(rmc_list[10])
#         else:
#             self.parsed['mag_var'] = -float(rmc_list[10])
#         self.parsed['qual'] = int(gga_list[6])
#         return True
