from datetime import datetime
import serial
import serial.tools.list_ports as list_ports
import struct
import threading
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from kivy.event import EventDispatcher
import time
from loguru import logger
from mip.export.csv_exporter import CSVExporter
from sys import platform

#############################################
#                 Constants                 #
#############################################

BOARD_DISCONNECTED = 0
"""
Board disconnected status.
"""

BOARD_FOUND = 1
"""
Board found but not connected status.
"""

BOARD_CONNECTED = 2
"""
Board connected status.
"""

START_STREAMING_CMD = "a"
"""
Command to start streaming data.
"""

STOP_STREAMING_CMD = "s"
"""
Command to stop streaming data.
"""


"""!
@brief Temperature and relative humidity set command.
"""
TEMP_RH_SETTINGS_SET_CMD = "x"

"""!
@brief Temperature and relative humidity latch command.
"""
TEMP_RH_SETTINGS_LATCH_CMD = "X"

SAMPLE_RATE_1_HZ_CMD = "1"
SAMPLE_RATE_10_HZ_CMD = "2"
SAMPLE_RATE_25_HZ_CMD = "3"
SAMPLE_RATE_50_HZ_CMD = "4"
SAMPLE_RATE_100_HZ_CMD = "5"

RETRIEVE_BME280_CONF_CMD = "g"

CONN_REQUEST_CMD = "v"

IN_VALVE_AND_PUMP_ON_OUT_VALVE_AND_PUMP_OFF_CMD = "h" #0x68
IN_VALVE_AND_PUMP_OFF_OUT_VALVE_AND_PUMP_ON_CMD = "y" #0x79
IN_AND_OUT_VALVE_AND_PUMP_ON_CMD = "e"
IN_AND_OUT_VALVE_AND_PUMP_OFF_CMD = "i"

TM_RAMP_CMD = "r"
TM_SQUARE_CMD = "q"
TM_SINE_CMD = "w"
TM_TRIANGLE_CMD = "t"
TM_SQ_TR_CMD = "c"
TM_5V_CMD = "O"
TM_0V_CMD = "o"


"""!
@brief Data packet header byte.
"""
DATA_PACKET_HEADER = 0xAA

"""!
@brief Data packet tail byte.
"""
DATA_PACKET_TAIL = 0xF0

"""!
@brief BME Configuration header byte.
"""
BME_CONF_PACKET_HEADER = 0xBB

"""!
@brief DBME Configuration tail byte.
"""
BME_CONF_PACKET_TAIL = 0xB0

"""!
@brief BME Configuration header byte.
"""
BME_SET_CONF_PACKET_HEADER = "t"

"""!
@brief DBME Configuration tail byte.
"""
BME_SET_CONF_PACKET_TAIL = "T"


class Singleton(type):
    """
    This class allows to implement the Singleton pattern.
    Using the Singleton class as metaclass allows to implement
    the Singleton pattern in each class.

    Usage:


    >>> class CustomSingleton(metaclass=Singleton):
    ...     pass


    This way, only one instance is created of the class, and
    every time the class is instantiated in an object, the
    same instance is returned.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MIPSerial(EventDispatcher, metaclass=Singleton):
    """
    Main class for serial communication.
    """

    connected = NumericProperty(defaultvalue=BOARD_DISCONNECTED)
    """
    NumericProperty holding the current board connection status.
    It is possible to bind this property to all the widgets that
    need to detect any change in the board connection status.
    """

    message_string = StringProperty("")
    """
    NumericProperty holding the last battery voltage read
    from the device. It is possible to bind this property
    to all the widgets that need to show the current 
    battery status of the device.
    """

    data_sample_rate = NumericProperty(defaultvalue=0.0)
    is_streaming = BooleanProperty(False)

    sample_rate_num_samples = NumericProperty(defaultvalue=0)

    bme280_humidity_oversampling = StringProperty("")
    bme280_temperature_oversampling = StringProperty("")
    bme280_pressure_oversampling = StringProperty("")
    bme280_standby_time = StringProperty("")
    bme280_iir_filter = StringProperty("")

    measurement_stage = StringProperty("")

    current_temperature_modulation = StringProperty("5V")

    save_data = BooleanProperty()

    def __init__(self, baudrate=115200):
        self.port_name = ""
        self.baudrate = baudrate
        self.read_state = 0
        self.packet_type = ""
        self.received_packet_time = 0
        self.samples_read = 0
        self.callbacks = []

        self.configure_exporter()

        find_port_thread = threading.Thread(target=self.find_port, daemon=True)
        find_port_thread.start()

    def configure_exporter(self):
        self.exporter = CSVExporter()
        self.bind(is_streaming=self.exporter.is_streaming)
        self.bind(save_data=self.exporter.getter("save_data"))
        self.bind(
            bme280_humidity_oversampling=self.exporter.setter(
                "bme280_humidity_oversampling"
            )
        )
        self.bind(
            bme280_temperature_oversampling=self.exporter.setter(
                "bme280_temperature_oversampling"
            )
        )
        self.bind(
            bme280_pressure_oversampling=self.exporter.setter(
                "bme280_pressure_oversampling"
            )
        )
        self.bind(bme280_iir_filter=self.exporter.setter("bme280_iir_filter"))
        self.bind(bme280_standby_time=self.exporter.setter("bme280_standby_time"))
        self.bind(measurement_stage=self.exporter.setter("measurement_stage"))
        self.bind(
            current_temperature_modulation=self.exporter.setter(
                "temperature_modulation"
            )
        )
        self.add_callback(self.exporter.add_packet)

    def add_callback(self, callback):
        """
        Append callback to the list of callbacks that
        are called upon the complete reception of a
        data packet from the device.

        Args:
            callback: the callback to be appended to the list
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def find_port(self):
        """!
        Find the serial port to which the device is connected.

        This function scans all the available serial ports until
        the one to which the device is connected is found. Once
        found, it attempts to connect to it.
        """
        mip_port_found = False
        while not mip_port_found:
            ports = list_ports.comports()
            for port in ports:
                mip_port_found = self.check_mip_port(port.device)
                if mip_port_found:
                    self.port_name = port.device
                    if self.connect() == 0:
                        break
                    else:
                        self.connected = BOARD_DISCONNECTED

    def check_mip_port(self, port_name):
        """
        Check if the port is the correct one.

        This function checks whether the port passed in as
        parameter correspons to a proper device.
        @param port_name name of the port to be checked.
        @return True if the port was found to be corrected.
        @return False if the port was not found to be corrected.
        """
        logger.debug("Checking: {}".format(port_name))
        time.sleep(2)
        try:
            port = serial.Serial(port=port_name, baudrate=self.baudrate)
            if port.is_open:
                port.write(CONN_REQUEST_CMD.encode("utf-8"))
                time.sleep(2)
                received_string = ""
                while port.in_waiting > 0:
                    received_string += port.read().decode("utf-8", errors="replace")
                if "$$$" in received_string:
                    logger.debug("Device found on port: {}".format(port_name))
                    port.close()
                    self.connected = BOARD_FOUND
                    time.sleep(3)
                    return True
        except serial.SerialException:
            return False
        except ValueError:
            return False
        return False

    def connect(self):
        for i in range(5):
            try:
                self.port = serial.Serial(port=self.port_name, baudrate=self.baudrate)
                if self.port.isOpen():
                    logger.debug("Device connected")
                    self.connected = BOARD_CONNECTED
                    time.sleep(0.5)
                    # Start thread for data reading
                    read_thread = threading.Thread(target=self.read_data)
                    read_thread.daemon = True
                    read_thread.start()
                    self.retrieve_bme280_configuration()
                    self.set_temperature_modulation_pattern(
                        self.current_temperature_modulation
                    )
                    return 0
            except serial.SerialException:
                pass
        return 1

    def start_streaming(self):
        """!
        @brief Start data streaming from the board.

        This function starts data streaming from the board.
        It also sets up a running thread to retrieve the
        data from the board, parse it and send it to the
        data receivers.
        """
        if self.connected == BOARD_CONNECTED:
            self.is_streaming = True
            self.samples_read = 0
            self.received_packet_time = 0
            self.temperature_received_packet_time = 0
            self.temp_rh_samples_read = 0
            self.data_sample_rate = "0.00"
            self.temperature_sample_rate = "0.00"
            try:
                self.port.write(START_STREAMING_CMD.encode("utf-8"))
                logger.debug("Starting data streaming")
            except:
                logger.critical("Could not write command to board")
        else:
            logger.critical("Board is not connected")

    def stop_streaming(self):
        """!
        @brief Stop data streaming from the board.
        This function stops data streaming from the
        board. This function sends the appropriate command
        to the board and stops the running thread.
        """
        if self.connected == BOARD_CONNECTED:
            try:
                self.port.write(STOP_STREAMING_CMD.encode("utf-8"))
                logger.debug("Stopping data streaming")
                self.is_streaming = False
                self.read_state = 0
            except:
                logger.critical("Could not write command to board")
        else:
            logger.critical("Board is not connected")

    def read_data(self):
        while self.connected == BOARD_CONNECTED:
            if self.port.in_waiting > 0:
                # READ STATE 0
                if self.read_state == 0:
                    b = self.port.read(1)
                    # Header byte
                    b = struct.unpack("B", b)[0]
                    if b == DATA_PACKET_HEADER or b == BME_CONF_PACKET_HEADER:
                        self.read_state = 1
                        if b == BME_CONF_PACKET_HEADER:
                            self.packet_type = "bme conf"
                        else:
                            self.packet_type = "data"
                # READ STATE 1
                elif self.read_state == 1:
                    if self.packet_type == "data":
                        # Packet counter
                        packet_counter = self.port.read(1)
                        packet_counter = struct.unpack("B", packet_counter)[0]
                    elif self.packet_type == "bme conf":
                        # Configurations from BME280
                        bme280_settings = self.port.read(5)
                        bme280_settings = struct.unpack("5B", bme280_settings)
                        self.bme280_humidity_oversampling = (
                            self.get_bme280_oversampling_conf_value(bme280_settings[0])
                        )
                        self.bme280_temperature_oversampling = (
                            self.get_bme280_oversampling_conf_value(bme280_settings[1])
                        )
                        self.bme280_pressure_oversampling = (
                            self.get_bme280_oversampling_conf_value(bme280_settings[2])
                        )
                        self.bme280_standby_time = (
                            self.get_bme280_standby_time_conf_value(bme280_settings[3])
                        )
                        self.bme280_iir_filter = self.get_bme280_iir_filter_conf_value(
                            bme280_settings[4]
                        )
                    self.read_state = 2
                # READ STATE 2
                elif self.read_state == 2:
                    if self.packet_type == "data":
                        # Resistance bytes
                        resistance_bytes = self.port.read(32)

                        # Unpack bytes
                        s_1 = struct.unpack("4B", resistance_bytes[:4])
                        s_2 = struct.unpack("4B", resistance_bytes[4:8])
                        s_3 = struct.unpack("4B", resistance_bytes[8:12])
                        s_4 = struct.unpack("4B", resistance_bytes[12:16])
                        s_5 = struct.unpack("4B", resistance_bytes[16:20])
                        s_6 = struct.unpack("4B", resistance_bytes[20:24])
                        s_7 = struct.unpack("4B", resistance_bytes[24:28])
                        s_8 = struct.unpack("4B", resistance_bytes[28:32])

                        # Convert resistance
                        res_s_1 = self.convert_voltage(s_1)
                        res_s_2 = self.convert_voltage(s_2)
                        res_s_3 = self.convert_voltage(s_3)
                        res_s_4 = self.convert_voltage(s_4)
                        res_s_5 = self.convert_voltage(s_5)
                        res_s_6 = self.convert_voltage(s_6)
                        res_s_7 = self.convert_voltage(s_7)
                        res_s_8 = self.convert_voltage(s_8)
                        self.read_state = 3
                    elif self.packet_type == "bme conf":
                        end_byte = self.port.read(1)
                        end_byte = struct.unpack("1B", end_byte)[0]
                        if end_byte == BME_CONF_PACKET_TAIL:
                            self.read_state = 0
                elif self.read_state == 3:
                    # Temperature and humidity

                    pressure_raw = self.port.read(4)
                    temperature_raw = self.port.read(4)
                    humidity_raw = self.port.read(4)

                    temperature_raw = struct.unpack("4B", temperature_raw)
                    humidity_raw = struct.unpack("4B", humidity_raw)
                    pressure_raw = struct.unpack("4B", pressure_raw)

                    temperature = self.convert_temperature(temperature_raw)
                    humidity = self.convert_humidity(humidity_raw)
                    pressure = self.convert_pressure(pressure_raw)
                    self.read_state = 4
                elif self.read_state == 4:
                    end_byte = self.port.read(1)
                    end_byte = struct.unpack("B", end_byte)[0]
                    if end_byte == DATA_PACKET_TAIL:
                        # Check CRC
                        self.read_state = 0
                        self.samples_read += 1
                        self.update_computed_sample_rate()
                        # Create packet and send it to the receiver callbacks
                        packet = DataPacket(
                            temperature=temperature,
                            humidity=humidity,
                            pressure=pressure,
                            s_1=res_s_1,
                            s_2=res_s_2,
                            s_3=res_s_3,
                            s_4=res_s_4,
                            s_5=res_s_5,
                            s_6=res_s_6,
                            s_7=res_s_7,
                            s_8=res_s_8,
                            packet_counter=packet_counter,
                        )
                        for callback in self.callbacks:
                            callback(packet)
                    else:
                        logger.critical("Skipped one packet")
                        self.read_state = 0
            time.sleep(0.001)

    def compute_num_samples_sample_rate(self, sample_rate):
        """
        Compute number of samples per second (frequency) based on the
        sample rate string. This is used to set the Numeric Property
        and propagate the change to all the widgets that depend
        on the sample rate of the received data (e.g. plots).

        Args:
            - sample_rate the sample rate string, in format 'xx Hz'
        """
        # Get only the first part of the string --> frequency
        frequency = sample_rate.split(" ")[0]
        self.sample_rate_num_samples = int(frequency)

    def update_computed_sample_rate(self):
        # Compute overall data sample rate
        if self.samples_read == 1:
            self.received_packet_time = datetime.now()
        if self.samples_read > 0 and self.samples_read % 10 == 0:
            curr_time = datetime.now()
            diff = curr_time - self.received_packet_time
            self.data_sample_rate = (self.samples_read) / diff.total_seconds()

    def retrieve_bme280_configuration(self):
        """
        Send command to the board to retrieve current BME280 configuration.

        This function sends a command to the board to retrieve the current
        configuration for the BME280 sensor.
        The response from the board is parsed in the main read data function.
        """
        logger.debug("Retrieving BME280 configuration from board")
        if self.port.is_open and self.connected == BOARD_CONNECTED:
            self.port.write(RETRIEVE_BME280_CONF_CMD.encode("utf-8"))
        else:
            logger.critical("Board not connected. Cannot retrieve BME280 Configuration")

    ###########################################
    #    Temperature and humidity settings    #
    ###########################################
    def get_bme280_conf_cmds(
        self,
        temperature_oversampling,
        humidity_oversampling,
        pressure_oversampling,
        stanby_time,
        iir_filter,
    ):
        """
        Based on the desired settings, this function returns a byte array
        containing the commands to be sent to the board to properly configure
        the temperature and relative humidity sensor.

        Args:
            - th_sample_rate: the sample rate to be set to the board
            - th_repeatability: the repeatability setting to be set to the board

        Returns:
            - byte array with commands to be sent to the board

        Usage:
        >>> cmds = get_temp_hum_config_cmd('0.5 Hz', 'Med')
        ... cmds
        ... bytearray(b' $')
        """
        oversampling_dict = {
            "Skipped": 0x00,
            "x1": 0x01,
            "x2": 0x02,
            "x4": 0x03,
            "x8": 0x04,
            "x16": 0x05,
        }
        stanby_time_dict = {
            "0.5": 0x00,
            "62.5": 0x01,
            "125": 0x02,
            "250": 0x03,
            "500": 0x04,
            "1000": 0x05,
            "10": 0x06,
            "20": 0x07,
        }
        iir_filter_dict = {
            "Filter off": 0x00,
            "2": 0x01,
            "4": 0x02,
            "8": 0x03,
            "16": 0x04,
        }
        return bytearray(
            [
                oversampling_dict[humidity_oversampling],
                oversampling_dict[temperature_oversampling],
                oversampling_dict[pressure_oversampling],
                stanby_time_dict[stanby_time],
                iir_filter_dict[iir_filter],
            ]
        )

    def get_bme280_iir_filter_conf_value(self, iir_filter):
        """
        Based on the settings, this function returns the proper
        strings representing temperature and humidity sample rate value
        and repeatabiity settings.

        Args:
            - th_sample_rate: sample rate value
            - th_repeatability: repeatability value

        Returns:
            - string with sample rate configuration
            - string with repetability configuration

        Usage:
        >>> values = get_temp_hum_config_value(0x20, 0x24)
        ... values
        ... '0.5 Hz', 'Med'

        """
        iir_filter_dict = {
            0x00: "Filter off",
            0x01: "2",
            0x02: "4",
            0x03: "8",
            0x04: "16",
        }

        # Return dictionary values
        return iir_filter_dict[iir_filter]

    def get_bme280_oversampling_conf_value(self, oversampling_val):
        oversampling_dict = {
            0x00: "Skipped",
            0x01: "x1",
            0x02: "x2",
            0x03: "x4",
            0x04: "x8",
            0x05: "x16",
        }
        return oversampling_dict[oversampling_val]

    def get_bme280_standby_time_conf_value(self, standby_time):
        stanby_time_dict = {
            0x00: "0.5",
            0x01: "62.5",
            0x02: "125",
            0x03: "250",
            0x04: "500",
            0x05: "1000",
            0x06: "10",
            0x07: "20",
        }
        return stanby_time_dict[standby_time]

    def set_bme280_settings(
        self,
        temperature_oversampling,
        humidity_oversampling,
        pressure_oversampling,
        stanby_time,
        iir_filter,
    ):
        logger.debug(
            f"Setting BME280 Configuration to {temperature_oversampling}-{humidity_oversampling}-{pressure_oversampling}-{stanby_time}-{iir_filter}"
        )
        try:
            cmds = self.get_bme280_conf_cmds(
                temperature_oversampling,
                humidity_oversampling,
                pressure_oversampling,
                stanby_time,
                iir_filter,
            )
        except:
            logger.critical("Invalid settings")
        if self.port.is_open and self.connected == BOARD_CONNECTED:
            self.port.write(BME_SET_CONF_PACKET_HEADER.encode("utf-8"))
            self.port.write(cmds)
            self.port.write(BME_SET_CONF_PACKET_TAIL.encode("utf-8"))
        else:
            logger.critical(
                "Board is not connected. Cannot update temperature settings."
            )

    def set_hydraulics(self, in_valve_and_pump, out_valve_and_pump):
        logger.debug("Updating hydraulics settings")
        # if self.port.is_open and self.connected == BOARD_CONNECTED:
        if (not in_valve_and_pump) and (not out_valve_and_pump):
            self.port.write(IN_AND_OUT_VALVE_AND_PUMP_OFF_CMD.encode("utf-8"))
        elif (in_valve_and_pump) and (not out_valve_and_pump):
            self.port.write(IN_VALVE_AND_PUMP_ON_OUT_VALVE_AND_PUMP_OFF_CMD.encode("utf-8"))
        elif (not in_valve_and_pump) and (out_valve_and_pump):
            self.port.write(IN_VALVE_AND_PUMP_OFF_OUT_VALVE_AND_PUMP_ON_CMD.encode("utf-8"))
        else:
            self.port.write(IN_AND_OUT_VALVE_AND_PUMP_ON_CMD.encode("utf-8"))

    def set_temperature_modulation_pattern(self, value):
        logger.debug(f"Setting temperature modulation pattern to {value}")
        if value == "5V":
            self.port.write(TM_5V_CMD.encode("utf-8"))
            self.current_temperature_modulation = "5V"
        elif value == "0V":
            self.port.write(TM_0V_CMD.encode("utf-8"))
            self.current_temperature_modulation = "0V"
        elif value == "Ramp":
            self.port.write(TM_RAMP_CMD.encode("utf-8"))
            self.current_temperature_modulation = "Ramp"
        elif value == "Square":
            self.port.write(TM_SQUARE_CMD.encode("utf-8"))
            self.current_temperature_modulation = "Square"
        elif value == "Sine":
            self.port.write(TM_SINE_CMD.encode("utf-8"))
            self.current_temperature_modulation = "Sine"
        elif value == "Triangle":
            self.port.write(TM_TRIANGLE_CMD.encode("utf-8"))
            self.current_temperature_modulation = "Triangle"
        elif value == "Sq+Tr":
            self.port.write(TM_SQ_TR_CMD.encode("utf-8"))
            self.current_temperature_modulation = "Sq+Tr"
        else:
            logger.critical(f"{value} is not a valid option for temperature modulation")

    ###################################################
    #               Data conversion                   #
    ###################################################

    def convert_temperature(self, raw_temperature):
        """!
        @brief Convert raw bytes into temperature.

        This function converts the bytes passed in as
        parameter to a proper temperature value. The
        temperature value is computed given the
        equation stated in the SHT85 datasheet.
        @param raw_temperature temperature bytes
        @return computed temperature value
        """
        temp = (
            raw_temperature[0] << 24
            | raw_temperature[1] << 16
            | raw_temperature[2] << 8
            | raw_temperature[3]
        ) / 100
        return temp

    def convert_humidity(self, raw_humidity):
        """
        Convert raw bytes into humidity value.

        This function converts the bytes passed in as
        parameter to a proper humidity value. The
        humidity value is computed given the
        equation stated in the SHT85 datasheet.

        Args:
            - raw_humidity: the raw humidity bytes to be converted
        Returns:
            - the proper humidity value
        """
        assert isinstance(raw_humidity, tuple)
        hum = (
            raw_humidity[0] << 24
            | raw_humidity[1] << 16
            | raw_humidity[2] << 8
            | raw_humidity[3]
        ) / 1000
        return hum

    def convert_pressure(self, raw_pressure):
        assert isinstance(raw_pressure, tuple)
        pressure = (
            raw_pressure[0] << 24
            | raw_pressure[1] << 16
            | raw_pressure[2] << 8
            | raw_pressure[3]
        ) / 100
        return pressure

    def convert_voltage(self, voltage):
        """
        Convert raw bytes into voltage.

        This function converts the bytes passed in as
        parameter to a proper voltage value.

        Args:
            - 4 bytes of voltage data

        Returns:
            - computed voltage value
        """
        assert isinstance(voltage, tuple)
        voltage_v = voltage[0] << 24 | voltage[1] << 16 | voltage[2] << 8 | voltage[3]
        return (voltage_v / pow(2, 16)) * 5


class DataPacket:
    """Data packet holding data received from board."""

    def __init__(
        self,
        packet_counter=0,
        temperature=0,
        humidity=0,
        pressure=0,
        s_1=0,
        s_2=0,
        s_3=0,
        s_4=0,
        s_5=0,
        s_6=0,
        s_7=0,
        s_8=0,
    ):
        self.packet_counter = packet_counter
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.resistance_values = [s_1, s_2, s_3, s_4, s_5, s_6, s_7, s_8]

    def get_packet_counter(self):
        return self.packet_counter

    def get_temperature(self):
        return self.temperature

    def get_humidity(self):
        return self.humidity

    def get_pressure(self):
        return self.pressure

    def get_resistance(self, channel_number=None):
        if channel_number == None:
            return self.resistance_values

        if channel_number < 0 or channel_number > 8:
            return 0
        else:
            return self.resistance_values[channel_number]

    def get_resistance_array(self):
        return self.resistance_values

    def __str__(self):
        st = f"[{self.packet_counter}] - {self.temperature:.2f} - "
        st += f"{self.humidity:.2f} - {self.pressure:.2f} - {self.resistance_values}"
        return st
