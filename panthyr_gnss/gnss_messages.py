# -*- coding: utf-8 -*-


class NMEAMessage:

    def __init__(self, raw_message: str):
        self.raw_msg = raw_message

    def _check_crc(self) -> bool:
        """NMEA string checksum.

        Last two characters of a NMEA string are a CRC check.
        XOR each character (binary ASCII representation) between $ and *.
        Convert to base 16 to get the CRC.

        Returns:
            bool: True if checksum is correct, False if not.
        """
        stripped_message: str = self.raw_msg[
            1:-3]  # only use part between '$' and '*CRC'

        crc: int = 0  # start value for CRC

        for character in stripped_message:
            crc ^= ord(
                character
            )  # xor each character with the previous CRC solution
        crc_result: str = str(hex(crc)[2:])
        return crc_result == self.raw_msg[-2:].lower()


class GGAMessage(NMEAMessage):

    def __init__(self, raw_message: str):
        """Example GGA string: $GPGGA,133933.000,5114.16147,N,00255.70634,E,1,09,1.0,011.91,M,47.1,M,,*66
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
        13 	Age of differential GPS data, Type 1 or Type 9. Null field when DGPS is not used.
        14 	Reference station ID, range 0000-4095.
                Null field when any ref. station ID is selected and no corrections are received.
        15  The checksum data
        """
        super().__init__(raw_message)


class RMCMessage(NMEAMessage):

    def __init__(self, raw_message: str):
        """Example RMC (Recommended minimum) string:
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
        (12) NMEA >=2.3: FAA mode indicator, might or might not be in the message depending on gps
                configuration. Code should work with either.
        12/13  Checksum
        """
        super().__init__(raw_message)

    def process(self) -> bool:
        return True
