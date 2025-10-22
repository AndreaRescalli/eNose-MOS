"""
Classes to handle Top, Bottom, and Lateral toolbars.
"""

from mip.communication.mserial import MIPSerial
import mip.communication
import mip.widgets.dialogs as dialogs
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
import time
import json
from pathlib import Path
from functools import partial

from loguru import logger


class BottomBar(BoxLayout):
    """ """

    message_label = ObjectProperty(None)
    connection_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BottomBar, self).__init__(**kwargs)
        self.board = MIPSerial()
        self.board.bind(connected=self.connection_event)

    def update_text(self, instance, value):
        self.message_label.text = value

    def update_str(self, value):
        self.message_label.text = value

    def connection_event(self, instance, value):
        if value == mip.communication.mserial.BOARD_FOUND:
            Clock.schedule_once(self.set_connection_label_bkg_yellow)
            self.connection_label.color = (0, 0, 0, 1)
        elif value == mip.communication.mserial.BOARD_CONNECTED:
            Clock.schedule_once(self.set_connection_label_bkg_green)
            self.connection_label.color = (1, 1, 1, 1)
        elif value == mip.communication.mserial.BOARD_DISCONNECTED:
            Clock.schedule_once(self.set_connection_label_bkg_red)
            self.connection_label.color = (1, 1, 1, 1)

    def set_connection_label_bkg_green(self, instance):
        self.connection_label.update_color(0, 0.5, 0, 0.7)

    def set_connection_label_bkg_red(self, instance):
        self.connection_label.update_color(1, 0, 0, 0.7)

    def set_connection_label_bkg_yellow(self, instance):
        self.connection_label.update_color(1, 1, 0, 0.7)


class ColoredLabel(Label):
    def update_color(self, r, g, b, a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(r, g, b, a)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Toolbar(BoxLayout):
    message_string = StringProperty("")
    streaming = BooleanProperty(False)

    # Export settings
    save_data = BooleanProperty(False)
    data_format = StringProperty("")
    data_path = StringProperty("")
    custom_header = StringProperty("")

    # Protocol settings
    cleaning_stage_duration = NumericProperty()
    measurement_stage_duration = NumericProperty()
    recovery_stage_duration = NumericProperty()

    # Hydraulics setting
    in_hydraulic_status = BooleanProperty(False)
    out_hydraulic_status = BooleanProperty(False)

    # Temperature modulation setting
    temperature_modulation_setting = StringProperty("")

    # GUI Objects
    tm_config = ObjectProperty(None)
    bme280_config = ObjectProperty(None)
    hydraulics = ObjectProperty(None)
    export_button = ObjectProperty(None)
    protocol_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.default_settings = {
            "save_data": False,
            "data_format": "txt",
            "data_path": str(Path.cwd() / "Data"),
            "custom_header": "",
            "cleaning_stage_duration": 5,
            "measurement_stage_duration": 10,
            "recovery_stage_duration": 5,
        }
        super(Toolbar, self).__init__(**kwargs)
        self.load_settings()

    def temp_rh_dialog(self):
        self.message_string = "BME280 Configuration"
        popup = dialogs.BME280ConfigurationDialog()
        popup.open()

    def export_data_dialog(self):
        self.message_string = "Configuring data export"
        self.load_settings()
        popup = dialogs.ExportDialog()
        popup.set_settings(
            self.save_data, self.data_format, self.data_path, self.custom_header
        )

        popup.bind(save_data=self.setter("save_data"))
        popup.bind(data_format=self.setter("data_format"))
        popup.bind(folder_path_value=self.setter("data_path"))
        popup.bind(custom_header_string=self.setter("custom_header"))
        popup.bind(ok_pressed=self.save_settings)
        popup.open()

    def save_settings(self, instance, value):
        logger.debug("Updating settings")
        settings_json = {
            "save_data": self.save_data,
            "data_format": self.data_format,
            "data_path": self.data_path,
            "cleaning_stage_duration": self.cleaning_stage_duration,
            "measurement_stage_duration": self.measurement_stage_duration,
            "recovery_stage_duration": self.recovery_stage_duration,
        }
        with open("settings.json", "w") as f:
            f.write(json.dumps(settings_json, indent=4))

    def load_settings(self):
        if Path("settings.json").exists():
            with open("settings.json", "r") as f:
                unchanged_settings = True
                self.current_settings = json.load(f)
                for setting in self.default_settings.keys():
                    if not (setting in self.current_settings.keys()):
                        self.current_settings[setting] = self.default_settings[setting]
                        unchanged_settings = False
            if not unchanged_settings:
                with open("settings.json", "w") as f:
                    f.write(json.dumps(self.current_settings, indent=4))
        else:
            self.current_settings = self.default_settings
        self.save_data = self.current_settings["save_data"]
        self.data_format = self.current_settings["data_format"]
        self.data_path = self.current_settings["data_path"]
        self.cleaning_stage_duration = self.current_settings["cleaning_stage_duration"]
        self.measurement_stage_duration = self.current_settings[
            "measurement_stage_duration"
        ]
        self.recovery_stage_duration = self.current_settings["recovery_stage_duration"]

    def is_streaming(self, instance, value):
        self.streaming = value
        self.bme280_config.disabled = value
        self.export_button.disabled = value
        self.tm_config.disabled = not value
        self.protocol_button.disabled = value

    def temperature_modulation_dialog(self):
        popup = dialogs.TemperatureModulationDialog()
        popup.set_selected(self.temperature_modulation_setting)
        popup.bind(selected=self.setter("temperature_modulation_setting"))
        popup.open()

    def hydraulic_setup_dialog(self):
        popup = dialogs.HydraulicSetupDialog()

        popup.bind(in_line_status=self.update_in_hydraulic_status)
        popup.bind(out_line_status=self.update_out_hydraulic_status)

        popup.set_in_hydraulic(self.in_hydraulic_status)
        popup.set_out_hydraulic(self.out_hydraulic_status)

        popup.open()

    def update_in_hydraulic_status(self, instance, value):
        self.in_hydraulic_status = value

    def update_out_hydraulic_status(self, instance, value):
        self.out_hydraulic_status = value

    def enable_widgets(self, enable):
        self.tm_config.disabled = enable
        self.bme280_config.disabled = not enable
        self.hydraulics.disabled = not enable
        self.export_button.disabled = not enable
        self.protocol_button.disabled = not enable

    def protocol_dialog(self):
        popup = dialogs.ProtocolConfigurationDialog()
        popup.bind(cleaning_stage_duration=self.setter("cleaning_stage_duration"))
        popup.bind(measurement_stage_duration=self.setter("measurement_stage_duration"))
        popup.bind(recovery_stage_duration=self.setter("recovery_stage_duration"))
        popup.set_settings(
            self.cleaning_stage_duration,
            self.measurement_stage_duration,
            self.recovery_stage_duration,
        )
        popup.bind(ok_pressed=self.save_settings)
        popup.open()


class CurrentSessionInformation(BoxLayout):
    current_stage = StringProperty("")
    cleaning_stage_duration = NumericProperty()
    measurement_stage_duration = NumericProperty()
    recovery_stage_duration = NumericProperty()
    is_streaming = BooleanProperty()

    overall_time = ObjectProperty()
    current_stage_time = ObjectProperty()
    current_stage_perc = ObjectProperty()

    def __init__(self, **kwargs):
        super(CurrentSessionInformation, self).__init__(**kwargs)
        self.stages = ["Cleaning", "Measurement", "Recovery"]
        self.stage_idx = 0
        self.scheduled_updated = False

    def on_is_streaming(self, instance, value):
        if value:
            self.stages_duration = {
                "Cleaning": self.cleaning_stage_duration * 60,
                "Measurement": self.measurement_stage_duration * 60,
                "Recovery": self.recovery_stage_duration * 60,
            }
            self.total_duration = (
                self.cleaning_stage_duration
                + self.measurement_stage_duration
                + self.recovery_stage_duration
            )
            self.stage_idx = 0
            self.current_stage = self.stages[self.stage_idx]
            self.stage_seconds_counter = 0
            self.session_seconds_counter = 0
            self.session_completed = False
            self.current_stage_time.text = f"{00:02d}:{00:02d}"
            self.overall_time.text = f"{00:02d}:{00:02d}"
            self.update_labels = Clock.schedule_interval(self.update_time, 1)
            self.scheduled_updated = True
        else:
            if self.scheduled_updated:
                Clock.unschedule(self.update_labels)

    def update_time(self, dt):
        if not self.session_completed:
            if self.stage_seconds_counter < self.stages_duration[self.current_stage]:
                self.stage_seconds_counter += 1
            else:
                if self.stage_idx < (len(self.stages) - 1):
                    self.stage_idx += 1
                    self.current_stage = self.stages[self.stage_idx]
                    self.stage_seconds_counter = 0
                else:
                    self.session_completed = True

            min, sec = divmod(self.stage_seconds_counter, 60)
            self.current_stage_time.text = f"{min:02d}:{sec:02d}"

        self.session_seconds_counter += 1
        min, sec = divmod(self.session_seconds_counter, 60)
        self.overall_time.text = f"{min:02d}:{sec:02d}"


class TopBar(BoxLayout):
    enable_buttons = BooleanProperty(False)
    streaming_button = ObjectProperty(None)
    battery_label = ObjectProperty(None)
    stage_selection_bar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TopBar, self).__init__(**kwargs)
        self.ser = MIPSerial()

    def streaming(self):
        """!
        @brief Callback called on streaming button pressed.

        This function checks whether the board is currently
        streaming data or not, and based on that triggers
        the start/stop of data streaming and also
        updates the text of the button.
        """
        if self.ser.is_streaming:
            self.ser.stop_streaming()
            self.streaming_button.text = "Start"
        else:
            self.ser.start_streaming()
            self.streaming_button.text = "Stop"

    def enable_widgets(self, enabled):
        """!
        @brief Enable/disable widgets for interaction with board.
        """
        self.streaming_button.disabled = not enabled
