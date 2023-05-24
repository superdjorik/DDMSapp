from kivymd.uix.screen import MDScreen

WIFI_CHANNELS = {1: 2412,
                 2: 2417,
                 3: 2422,
                 4: 2427,
                 5: 2432,
                 6: 2437,
                 7: 2442,
                 8: 2447,
                 9: 2452,
                 10: 2457,
                 11: 2462,
                 12: 2467,
                 13: 2472,
                 14: 2484,
                 }
ser_data_test = {'Channel': [7, 11],
                 'RSSI': [-39, -47]}

def wifi_channel_to_freq(wifi_channel):
    return WIFI_CHANNELS.get(wifi_channel)

# def print_wifi(wifi_freq, rssi_power):
#     class Linechart(MDScreen):
#         def update(self):
#             chart1 = self.ids.chart1
#             chart1.x_values = wifi_freq
#             chart1.y_values = rssi_power
#             chart1.update()




