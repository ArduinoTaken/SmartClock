import serial
import serial.tools.list_ports
import serial.tools.list_ports_linux
import os
import platform
import glob
import re


def find_usb_tty():
    tty_list=[]

    try:
        ports_comports=serial.tools.list_ports_linux.comports()
        for i in range(0,len(ports_comports)):
            temp_list=list(ports_comports[i])
            print(temp_list)
            tty_item={"name":"NA",
                      "addr":"NA"}
            tty_item["addr"] = temp_list[0]
            tty_item["name"] = temp_list[1]
            tty_list.append(tty_item)
        print(tty_list)
    except Exception as e:
        print(e)

    return tty_list


def scanSerilPort():
    port_list=[]

    # window or Mac OS
    if platform.system() == "Windows" or platform.system() == "Darwin":
        ports_comports = serial.tools.list_ports.comports()
        for i in range(0,len(ports_comports)):
            temp_list=list(ports_comports[i])
            print("temp_list:" +str(temp_list))
            tty_item={"name":"NA",
                      "addr":"NA"}
            tty_item["addr"] = temp_list[0]
            tty_item["name"] = temp_list[1]
            port_list.append(tty_item)
        print(port_list)
        return port_list
    elif platform.system() == "Linux":
        return find_usb_tty()
    else:
        print('not match platform:%s' %str(platform.system()))
        return []

if __name__ == '__main__':
    port_list=scanSerilPort()
    print("================result==============")
    print(port_list)
