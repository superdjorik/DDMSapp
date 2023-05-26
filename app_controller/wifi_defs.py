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

def remove_wifi_duplicates(wifi_channel: list, wifi_rssi:list):
    res = {'Channel': [], 'RSSI': []}
    for x in range(len(wifi_channel)):
        # print(x)
        if wifi_channel[x] not in res['Channel']:
            res['Channel'].append(wifi_channel[x])
            res['RSSI'].append(wifi_rssi[x])
    return res


