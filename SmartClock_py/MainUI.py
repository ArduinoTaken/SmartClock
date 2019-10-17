# coding:UTF-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import time
from tkinter import messagebox
import threading
import queue
import sys
import platform
import os

import serial.tools.list_ports_linux
import serial.tools.list_ports
import serial


class ArduinoMicro(object):
    """docstring for ArduinoMicro"""

    def __init__(self,receivedData):
        super(ArduinoMicro, self).__init__()

        self.isMonitor = True
        self.isExitOk = False
        self.receivedData = receivedData
        self.setup()
        self.openArduino()

    def setup(self):
        serial_list=self.scanSerilPort()
        if len(serial_list) < 1:
            print("No any serial ports!")
            exit(-1)
        find_arduino = False
        self.serialName = "NA"
        for item in serial_list:
            if item["name"].upper().find("ARDUINO") != -1:
                find_arduino = True
                self.serialName = item["addr"]
                break
        if not find_arduino:
            print("No find arduino micro!")
            exit(-1)
        print("find Arduino micro port:" +self.serialName)

    def openArduino(self):
        self.opened = False
        try:
            self.serial = serial.Serial(self.serialName, 9600, timeout=2.0)
            if self.serial.isOpen():
                self.opened = True
                self.monitorArduino()
        except Exception as e:
            self.opened = False
        print("open arduino status:" +str(self.opened))

    def closeArduino(self):
        self.isMonitor = False
        while not self.isExitOk:
            time.sleep(0.1)
        self.serial.close()
        print("arduino closed")
        return True

    def monitorArduino(self):
        # 开启计时线程
        t = threading.Thread(target=self.monitorArduinoThread)
        t.setDaemon(True)
        t.start()

    def monitorArduinoThread(self):
        time.sleep(2.0)
        while self.isMonitor:
            read_data=self.readLine()
            self.receivedData(read_data)
        self.isExitOk = True

    def readLine(self):
        Response = ""
        startTime=time.time()
        while ((time.time() - startTime) < 1.0):
            time.sleep(0.01)
            tempStr = self.serial.read().decode('utf-8')
            #print("tempStr:" +tempStr)
            Response += tempStr
            if tempStr.find('\n') != -1:
                print('[RX]' + Response)
                return Response
        return "TIMEOUT"

    def find_usb_tty(self):
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

    def scanSerilPort(self):
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
            return self.find_usb_tty()
        else:
            print('not match platform:%s' %str(platform.system()))
            return []


class SmartClock(object):
    """docstring for SmartClock"""

    def __init__(self):
        super(SmartClock, self).__init__()

        self.init()
        self.loadLabels()

        self.Arduino=ArduinoMicro(self.receivedArduinoData)

        self.updateUIQueue = queue.Queue()
        self.updateUIloop()

        self.refreshTime()
        self.master.mainloop()

    def init(self):
        # 获取运行平台的名称
        self.sysName = platform.system()  # "Windows"/"Darwin"/"Linux"
        # print(sys.path[0])
        # :/Users/weidongcao/Documents/PythonCode/SSTester

        self.master = Tk()
        # w, h = self.master.maxsize()
        # self.master.geometry("{}x{}".format(w,h))
        self.max_width=self.master.winfo_screenwidth()
        self.max_height=self.master.winfo_screenheight()
        self.master.geometry('950x750')  # 是x 不是*
        self.master.resizable(width=True, height=True)  # 宽不可变, 高可变,默认为True
        self.master.attributes("-fullscreen", True)

        self.timeStr=StringVar()
        self.temperatureStr=StringVar()
        self.humidityStr=StringVar()

        self.logStr=StringVar()

        self.timeStr.set("12:23")
        self.temperatureStr.set("27.35C")
        self.humidityStr.set("60.10%")
        self.logStr.set("this is log string............")

        self.screenIsLight = True
        self.startTime = time.time()
        self.deltaTime = 60.0
        self.refreshTimeCount = 0

    def loadLabels(self):
        frame1 = tk.Frame(self.master, bg="black", relief=tk.SOLID,)
        # self.lf.pack(expand=NO, padx=self.x, pady=self.y)
        frame1.place(x=0, y=0, width=self.max_width, height=self.max_height)

        # 指定字体名称、大小、样式
        # ft = tkFont.Font(family='Fixdsys', size=28, weight=tkFont.NORMAL)

        # 创建Label，设置背景色和前景色
        self.timeLabel = Label(frame1,
                               textvariable=self.timeStr,
                               fg='gray',
                               font="Arial 248",  # ft
                               bg="black")
        # 使用place()设置该Label的大小和位置
        self.timeLabel.place(x=50, y=50, width=900, height=300)

        # 创建Label，设置背景色和前景色
        self.temperatureLabel = Label(frame1,
                                      textvariable=self.temperatureStr,
                                      fg='gray',
                                      font="Arial 86",
                                      bg="black")
        # 使用place()设置该Label的大小和位置
        self.temperatureLabel.place(x=500, y=370, width=400, height=100)

        # 创建Label，设置背景色和前景色
        self.humidityLabel = Label(frame1,
                                   textvariable=self.humidityStr,
                                   fg='gray',
                                   font="Arial 86",
                                   bg="black")
        # 使用place()设置该Label的大小和位置
        self.humidityLabel.place(x=500, y=490, width=400, height=100)

        # 创建Label，设置背景色和前景色
        self.logLabel = Label(frame1,
                              textvariable=self.logStr,
                              fg='gray',
                              font="Arial 10",
                              bg="black")
        # 使用place()设置该Label的大小和位置
        self.logLabel.place(x=200, y=650, width=500, height=30)

        # 新建一个按钮
        self.Quit_btn = Button(frame1,
                               text='Quit',
                               bg="gray",
                               command=self.quitBtnClick)  # 背景色:蓝色

        self.Quit_btn.place(x=800, y=700, width=60, height=20)

    def quitBtnClick(self):
        self.updateUIQueue.put((1,"QUIT"))

    def quitThread(self):
        self.Arduino.closeArduino()
        print("all closed ok")
        self.master.destroy()

    def receivedArduinoData(self,data):
        print("[SC-RX]" +data)
        self.updateUIQueue.put((0, data))

    # 刷新UI队列loop(主线程)
    def updateUIloop(self):
        # self.myLogger.logger.warn(threading.currentThread().getName())
        # print('update ui loop...%d',self.index)
        self.refreshTimeCount+=1
        if self.refreshTimeCount > 50:
            self.refreshTimeCount = 0
            print("will refresh current time...")
            self.refreshTime()

        while self.updateUIQueue.qsize():
            try:
                msg = self.updateUIQueue.get(0)
                if msg[0] == 0:
                    log = msg[1].strip()
                    self.logStr.set(log)
                    self.actionGo(log)
                    # self.logLabel.update()
                if msg[0] == 1:
                    self.quitThread()
                    return

            except Exception as e:
                print(str(e))

        self.master.after(100, self.updateUIloop)

    def actionGo(self,data):
        if data.find("[HUMAN]") != -1:
            isHuman = False
            if data.find("[HUMAN]:1") != -1:
                isHuman = True
            print("will refresh screen light...")
            self.lightScreen(isHuman)
        elif data.find("[Humidity]") != -1:
            self.refreshTH(data)

    def lightScreen(self,isHuman):
        if isHuman:
            self.startTime = time.time()
            if not self.screenIsLight:
                print("will turn on screen...")
                os.system("xset dpms force on")
                self.screenIsLight = True
        else:
            if time.time() - self.startTime < self.deltaTime:
                print("delta time is less")
                return
            self.startTime = time.time()
            if self.screenIsLight:
                os.system("xset dpms force off")
                print("will turn off screen...")
                self.screenIsLight = False

    def refreshTH(self,log):
        try:
            data_arr=log.split(';')
            temStr=data_arr[1].split(':')[1] +"C"
            humStr=data_arr[0].split(':')[1]
            humStr=humStr.replace(' ','')
            self.temperatureStr.set(temStr)
            self.humidityStr.set(humStr)
        except Exception as e:
            print(str(e))

    def refreshTime(self):
        nowTime=time.strftime('%H:%M', time.localtime(time.time()))
        self.timeStr.set(nowTime)

if __name__ == '__main__':
    mySmartClock=SmartClock()
    # myArduino=ArduinoMicro()


