# ---------------------------------------------------------------------#
# Name - IR&NECDataCollect.py
# Description - Reads data from the IR sensor but uses the official NEC Protocol (command line version)
# Author - Lime Parallelogram
# Licence - Attribution Lime
# Date - 06/07/19 - 18/08/19
# ---------------------------------------------------------------------#
# Imports modules
import os
import threading

# ==================#
# Promps for values
# Input pin
import gpio

PIN_IN = 11


class KeyConfig:
    def __init__(self, file_name: str):
        self.file_name = file_name
        file_out = open(file_name, 'a')
        file_out.close()
        self.code_to_name = self.__read_all__()

    def write_key(self, key_code, key_name):
        output = open(self.file_name, 'a')
        output.write("{0}={1}\n".format(key_code, key_name))
        output.close()
        self.code_to_name[key_code] = key_name

    def __read_all__(self):
        file_in = open(self.file_name, 'r')
        lines = file_in.readlines()
        hex_keys = {}
        for line in lines:
            if line.replace(" ", "").__len__() == 0:
                continue
            keys = line.split("=")
            if len(keys) < 2:
                continue
            hex_keys[keys[0].strip()] = keys[1].strip()
        file_in.close()
        return hex_keys

    def print(self):
        config = self.code_to_name
        for key in config:
            print("key {0} -> {1}".format(key, config[key]))


key_config = KeyConfig("config.cnf")
is_develop = False
if is_develop:
    remote = gpio.SimulateIRRemote(port_number=PIN_IN)
else:
    remote = gpio.RaspIRRemote(port_number=PIN_IN)


def training():
    while True:
        if input("Press enter to start. Type q to quit. ") == 'q':
            break
        key_hex = remote.wait_key_press()
        button_name = input("Enter a name for this button: ")
        key_config.write_key(key_hex, button_name)


def on_key_event(key_code):
    if not key_config.code_to_name.__contains__(key_code):
        print("Not found key {0}".format(key_code))
        return

    key_name = key_config.code_to_name[key_code]
    print("You're press {0} = key {1}".format(key_code, key_name))

    event = {
        "top": lambda: os.system("nohup /usr/bin/chromium-browser www.google.com >/dev/null &"),
        "bottom": lambda: os.system("ps ax | grep chromium-browser | awk '{print $1}' | xargs kill"),
        "left": lambda: os.system("nohup vlc /media/pi/MyStorage/Videos/i-bet-you-think-about-me.mp4 >/dev/null &"),
        "right": lambda: os.system("ps ax | grep vlc | awk '{print $1}' | xargs kill")
    }
    if event.__contains__(key_name):
        threading.Thread(target=lambda: event[key_name]()).start()


if __name__ == "__main__":

    options = input("Options:\t\n"
                    "1. Training\n"
                    "2. Listen\n"
                    "3. Exit\n"
                    "4. Show config\n"
                    "Press here: ")

    action = {
        "1": lambda: training(),
        "2": lambda: remote.start_listen_key_press(on_key_event=on_key_event),
        "3": lambda: exit(0),
        "4": key_config.print
    }

    try:
        action[options]()
    except Exception as e:
        print("Error {0}".format(e))
    finally:
        remote.release()
        exit(0)
