import json
import re

import numpy as np
from kivy.logger import LoggerHistory
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import mainthread
from kivy.utils import platform
import threading
import sys
from kivy.garden.graph import Graph, MeshLinePlot
from math import sin

from app_controller.wifi_defs import wifi_channel_to_freq

if platform == 'android':
    from usb4a import usb
    from usbserial4a import serial4a
else:
    from serial.tools import list_ports
    from serial import Serial, SerialException


class DroneDetector(MDApp):
    def __init__(self, *args, **kwargs):
        self.uiDict = {}
        self.device_name_list = []
        self.serial_port = None
        self.read_thread = None
        self.port_thread_lock = threading.Lock()
        super(DroneDetector, self).__init__(**kwargs)

    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file('dronedetector.kv')

    def on_stop(self):
        if self.serial_port:
            with self.port_thread_lock:
                self.serial_port.close()

    def on_btn_scan_release(self):
        self.uiDict['box_list'].clear_widgets()
        self.device_name_list = []

        if platform == 'android':
            usb_device_list = usb.get_usb_device_list()
            self.device_name_list = [
                device.getDeviceName() for device in usb_device_list
            ]
        else:
            usb_device_list = list_ports.comports()
            self.device_name_list = [port.device for port in usb_device_list]

        for device_name in self.device_name_list:
            btnText = device_name
            button = Button(text=btnText, size_hint_y=None, height='100dp')
            button.bind(on_release=self.on_btn_device_release)
            self.uiDict['box_list'].add_widget(button)

    def on_btn_device_release(self, btn):
        device_name = btn.text

        if platform == 'android':
            device = usb.get_usb_device(device_name)
            if not device:
                raise SerialException(
                    "Device {} not present!".format(device_name)
                )
            if not usb.has_usb_permission(device):
                usb.request_usb_permission(device)
                return
            self.serial_port = serial4a.get_serial_port(
                device_name,
                115200,
                8,
                'N',
                1,
                timeout=1
            )
        else:
            self.serial_port = Serial(
                device_name,
                115200,
                8,
                'N',
                1,
                timeout=1
            )

        if self.serial_port.is_open and not self.read_thread:
            self.read_thread = threading.Thread(target=self.read_msg_thread)
            self.read_thread.start()

        self.uiDict['sm'].current = 'screen_main'
        self.plot_chart()
        # self.update_chart()

    def on_btn_write_release(self):
        if self.serial_port and self.serial_port.is_open:
            if sys.version_info < (3, 0):
                data = bytes(self.uiDict['txtInput_write'].text + '\n')
            else:
                data = bytes(
                    (self.uiDict['txtInput_write'].text + '\n'),
                    'utf8'
                )
            self.serial_port.write(data)
            self.uiDict['txtInput_read'].text += '[Sent]{}\n'.format(
                self.uiDict['txtInput_write'].text
            )
            self.uiDict['txtInput_write'].text = ''


    def read_msg_thread(self):
        while True:
            try:
                with self.port_thread_lock:
                    if not self.serial_port.is_open:
                        break
                    received_msg = self.serial_port.read(self.serial_port.in_waiting)
                if received_msg:
                    msg = received_msg.decode('utf8')
                    self.display_received_msg(msg)
            except Exception as ex:
                raise ex

    @mainthread
    def update_batt_level(self, lvl):
        self.uiDict['batt_level'].text = lvl

    @mainthread
    def update_wifi_channels(self, wifi_lvl):
        self.uiDict['wifi_level'].text = wifi_lvl


    @mainthread
    def display_received_msg(self, msg):
        self.uiDict['txtInput_read'].text += msg

        lastline = list(reversed(self.uiDict['txtInput_read'].text.split('\r\n')))[0]
        # print(f'line {lastline}')
        wifi_found = re.findall(r'(\{.*\})', lastline)
        batt_level = re.findall(r'(?<=Battery Voltage = )\d\.\d\d', lastline)
        if len(wifi_found) > 0:
            founded = json.loads(wifi_found[-1])
            self.update_wifi_channels(wifi_found[-1])
            # print((founded['Channel']))
            # for x in range(len(founded['Channel'])):
            self.update_chart(founded['Channel'], founded['RSSI'])
                # print(founded['Channel'], founded['RSSI'])

        if len(batt_level) > 0:
            self.update_batt_level(batt_level[-1])

    @mainthread
    def plot_chart(self):
        self.uiDict['chart'].clear_widgets()
        # self.uiDict['btn_chart'].clear_widgets()
        self.graph = Graph(
            xlabel='Частота', ylabel='Уровень',
            # x_ticks_minor=10,
                      x_ticks_major=10, y_ticks_major=10,
                      y_grid_label=True, x_grid_label=True, padding=5,
                      x_grid=True,
                      y_grid=True,
                      xmin=2400,
                      xmax=2500,
                      ymin=-100,
                      ymax=0
        )
        # self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        # self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
        # self.graph.add_plot(self.plot)
        self.uiDict['chart'].add_widget(self.graph)

    def update_chart(self, wifi_chan, wifi_rssi):
        # self.uiDict['chart'].clear_widgets()
        for plot in self.graph.plots:
            self.graph.remove_plot(plot)


        for i in range(len(wifi_chan)):
            self.i = MeshLinePlot(color=[1, 0, 0, 1])
            chan = wifi_channel_to_freq(wifi_chan[i])
            rssi = wifi_rssi[i]
            left = chan - 20
            right = chan + 20
            x = np.linspace(left, right, 50)
            self.i.points = [(x, -99 - (-99 - rssi) * np.sin((x - chan + 20) / 40 * np.pi)) for x in range(left, right+1)]
            self.graph.add_plot(self.i)
        # self.uiDict['chart'].update_widget(self.graph)



if __name__ == '__main__':
    DroneDetector().run()
