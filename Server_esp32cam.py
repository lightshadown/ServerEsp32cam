#chat gpt version 
import sys, os, socket
from datetime import datetime
from threading import Thread
import netifaces as nt
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QApplication
import pigpio as pp

port = 7500

class VideoRec(QThread):
    new_frm = pyqtSignal(bytes)
    Log_signal = pyqtSignal(str)
    
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.is_running = True
    
    def run(self):
        self.Log_signal.emit("Starting Socket")
        #self.log("starting socket")
        buffer = b''
        tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Log_signal.emit("after socket")
        #self.log("after socket")
        # host = socket.gethostname()
        # ip = socket.gethostbyname(host)
        
        # self.log("sup")
        # self.log("socket ip {0} and hostname {1}".format(ip, host))
        try:
            wi_ip = nt.ifaddresses('wlan0')[nt.AF_INET][0]['addr']
            self.Log_signal.emit("socket ip {0}".format(wi_ip))
            #self.log("socket ip {0}".format(wi_ip))
            tunnel.bind((wi_ip, self.port))
            tunnel.listen(3)
            self.Log_signal.emit("Only recieving data")
            clntunnel, addrs = tunnel.accept() 
            self.Log_signal.emit("coneccted to ip: {0} on port: {1}".format(addrs[0], addrs[1] ))
            while self.is_running:
                try:
                    data = clntunnel.recv(1024)    # check recv(1024).decode("utf-8")
                    if not data: 
                        #self.Log_signal.emit("no data")
                        break
                    buffer += data
                    
                    while True:
                        #self.Log_signal.emit("inside while")
                        #frame, buffer = self.jpeg_EoL(buffer)
                        frame, buffer = self.extract_jpeg(buffer)
                        #self.log("Checking")
                        if frame is None:
                            #self.Log_signal.emit("no data on frame")
                            break
                        self.new_frm.emit(frame)
                        #self.Log_signal.emit("end of while")
                        #break        
                except socket.error as e:
                    self.Log_signal.emit("Socket error: {0}".format(e))
                    #self.log("Someting went wrong, no conecction")
                    break
        except socket.error as e:
            self.Log_signal.emit("Socket error: {0}".format(e))
    
    # this one works fine    
    # def run(self):
    #     self.Log_signal.emit("Starting Socket")
    #     #self.log("starting socket")
    #     buffer = b''
    #     tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.Log_signal.emit("after socket")
    #     #self.log("after socket")
    #     # host = socket.gethostname()
    #     # ip = socket.gethostbyname(host)
        
    #     # self.log("sup")
    #     # self.log("socket ip {0} and hostname {1}".format(ip, host))
    #     try:
    #         wi_ip = nt.ifaddresses('wlan0')[nt.AF_INET][0]['addr']
    #         self.Log_signal.emit("socket ip {0}".format(wi_ip))
    #         #self.log("socket ip {0}".format(wi_ip))
    #         tunnel.bind((wi_ip, self.port))
    #         tunnel.listen(3)
            
    #         clntunnel, addrs = tunnel.accept() 
    #         self.Log_signal.emit("coneccted to ip: {0} on port: {1}".format(addrs[0], addrs[1] ))
    #         #self.log("conected to ip: {0} on port: {1}".format( addrs[0],addrs[1] ) )
    #         while self.is_running:
    #             try:
    #                 data = clntunnel.recv(1024)    # check recv(1024).decode("utf-8")
    #                 if not data: 
    #                     self.Log_signal.emit("no data")
    #                     break
    #                 buffer += data
    #                 #if not buffer:
    #                 #    self.log("No data on buffer")
    #                 # else:
    #                 #     self.log("new data")
    #                 #self.Log_signal.emit("before while")
    #                 while True:
    #                     #self.Log_signal.emit("inside while")
    #                     #frame, buffer = self.jpeg_EoL(buffer)
    #                     frame, buffer = self.extract_jpeg(buffer)
    #                     #self.log("Checking")
    #                     if frame is None:
    #                         #self.Log_signal.emit("no data on frame")
    #                         break
    #                     else: 
    #                         try:
    #                             send_text = "ESP_OK".encode("utf-8")
    #                             clntunnel.send(send_text)
    #                         except socket.error as e:
    #                             self.Log_signal.emit("cannont send confirmation error: {0}".format(e))
    #                             break
                        
    #                     response = clntunnel.recv(10).decode("utf-8", errors="replace")
    #                     #response = response.decode()
    #                     # check encoding on the esp32cam
    #                     if response is None:
    #                         self.Log_signal.emit("not recieved confirm")
    #                         break
    #                     self.Log_signal.emit(response)
    #                     if "ESP_OK" in response:
    #                         self.Log_signal.emit("Ok: {0}".format(response))
    #                         self.new_frm.emit(frame)
    #                     if "ESP_ERROR" in response:
    #                         self.Log_signal.emit("confirmation error: {0}".format(response))
    #                         break
    #                     self.Log_signal.emit("end of while")
    #                     #break        
    #             except socket.error as e:
    #                 self.Log_signal.emit("Socket error: {0}".format(e))
    #                 #self.log("Someting went wrong, no conecction")
    #                 break
    #     except socket.error as e:
    #         self.Log_signal.emit("Socket error: {0}".format(e))
    
    def stop(self):
        self.is_running = False
        
    def extract_jpeg(self, buffer):
        start = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9')
        if start != -1 and end !=-1:
            jpeg = buffer[start:end+2]
            buffer = buffer[end+2:]
            return jpeg, buffer
        else:
            return None, buffer
    
    def jpeg_EoL(self, buffer):
        inicio = 0
        postn = buffer.find(b'\n', inicio)
        if postn == -1:
            return None, buffer    # not found
            
        if postn != -1:
            frame = buffer[inicio:postn]
            buffer = buffer[postn + 1:]
            return frame, buffer
        else:
            return None, buffer
            
            
class VideoStrRecv(QWidget):
    def __init__(self, port):
        super().__init__()
        self.cam1 = QLabel("HELLO", alignment=Qt.AlignCenter)  #cam1
        self.cam1.setStyleSheet("font-size:90px; font-weight:bold; color:Black; border: 1px solid black;")
        self.Video = VideoRec(port)
        self.Video.new_frm.connect(self.update_frame)
        self.Video.Log_signal.connect(self.Logging)

        layout = QHBoxLayout(self)
        layout.addWidget(self.cam1)
        self.setLayout(layout)
    
    def start_this_shiat(self):
        self.log("starting thread")
        self.Video.start()
        
    def update_frame(self, frame):
        self.log("update frame")
        q_image = QImage.fromData(frame)
        pismap = QPixmap.fromImage(q_image)
        #pismap.scaled(300,226, Qt.KeepAspectRatio)
        self.cam1.setPixmap(pismap)
        self.cam1.setFixedWidth(800)
        self.cam1.setFixedHeight(600)
    
    def log(self, datalog):
        try:
            with open("LogTrilla2.txt","a") as file:
                file.write("{0} -- {1}\n".format(datetime.now().strftime("%H:%M %d-%m-%Y"), datalog))
        except Exception as a:
            print(f"Error on log file {a}")
    
    def Logging(self, error):
        self.log("- {0}".format(error))


if __name__ == "__main__":
    print ('program start')
    app = QApplication([])
    w = VideoStrRecv(port)
    w.log("--------------\nStarting Screen")
    w.resize(1024,530) # X,Y
    #w.showFullScreen()    # setfor later, fullscreen
    #w.setWindowFlag(Qt.FramelessWindowHint)
    w.setWindowTitle("You son of a biatch")
    #w.setWindowIcon(QIcon('novideo.png'))
    w.show()
    w.start_this_shiat()
    sys.exit(app.exec_())