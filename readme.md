serial port app based on https://github.com/jacklinquan/usbserial4a

kivy installation:

```
pip install kivy[base] kivy_examples --pre --extra-index-url https://kivy.org/downloads/simple/
```
OR use python <=3.10 instead of 3.11



kv syntax highliting in pycharm for Windows (File - Manage IDE - Import): 

https://github.com/noembryo/KV4Jetbrains

#adb:
adb tcpip 555
adb connect 192.168.1.19:5555
adb logcat > log.txt

#clean buildozer
rm -rf .buildozer ~/.buildozer