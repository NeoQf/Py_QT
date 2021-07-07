import sys
import numpy as np
import cv2
import math
from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap,QFont,QIcon
from PyQt5.QtWidgets import (QApplication,QDialog, QFileDialog, QGridLayout,
                QLabel, QPushButton,QHBoxLayout,QFrame,QWidget,QLineEdit)
import time 
import os
import FireDetect #加载FireDetect火焰检测模块
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"



class MainWindow(QWidget):
    def __init__(self):

        # 初始化一个img, 用于存储图像
        self.img = None
        self.timer_camera = QtCore.QTimer()
        self.cap = cv2.VideoCapture()
        self.CAM_NUM = 0
        self.detect_flag = 0

        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon('opencv.png'))
        self.resize(800, 600)#主窗体大小
        #-----------标题设置------------#
        self.title = QLabel('这里改成自己的标题', self)
        self.title.move(10, 20)
        self.title.setFont(QFont("楷体",36))
        #-----------主预览窗口----------#
        self.label = QLabel(self)
        self.label.resize(640,480)
        self.label.move(10,105)
        self.label.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.label.setScaledContents(True)
        
        #-----------按键相关设置----------#
        self.btnOpenCam = QPushButton('摄像头检测', self)
        self.btnOpenCam.setGeometry(QtCore.QRect(660,105,130,45))
        self.btnOpenCam.setFont(QFont("微软雅黑",13))

        self.btnOpenVideo = QPushButton('视频检测', self)
        self.btnOpenVideo.setGeometry(QtCore.QRect(660,105+60,130,45))
        self.btnOpenVideo.setFont(QFont("微软雅黑",13))
      
        self.btnClose = QPushButton('关闭检测', self)
        self.btnClose.setGeometry(QtCore.QRect(660,105+120,130,45))
        self.btnClose.setFont(QFont("微软雅黑",13))

        self.btnImgTest = QPushButton('图片检测', self)
        self.btnImgTest.setGeometry(QtCore.QRect(660,105+180,130,45))
        self.btnImgTest.setFont(QFont("微软雅黑",13))
        
        self.btnQuit = QPushButton('退出系统', self)
        self.btnQuit.setGeometry(QtCore.QRect(660,105+240,130,45))
        self.btnQuit.setFont(QFont("微软雅黑",13))
        
        self.btnClose.setEnabled(False)
         
        # 信号与槽连接, PyQt5与Qt5相同, 信号可绑定普通成员函数
        self.btnOpenCam.clicked.connect(self.OpenCam)
        self.btnOpenVideo.clicked.connect(self.OpenVideo)
        self.btnImgTest.clicked.connect(self.ImgTest)
        self.btnClose.clicked.connect(self.CloseTest)
        self.btnQuit.clicked.connect(self.QuitApp)      
        
        #self.timer_camera.timeout.connect(self.show_camera)
        self.video_flag = 1
        self.flag = 0

    def QuitApp(self):
        self.close()

    def show_camera(self):
        flag, self.img = self.cap.read()
        if self.img is not None:
            if self.detect_flag == 0: #只显示视频画面
                self.showViewImg(self.label,self.img)
            elif self.detect_flag == 1: #手势识别
                self.GestureRecognition(self.img)
            elif self.detect_flag == 2: #手势跟踪
                self.GestureTrack(self.img)

    # 摄像头火焰检测    
    def OpenCam(self):
        print("摄像头火焰检测")
        self.flag = 0
        self.video_flag = 1
        self.ccd=FireDetect.Work(self)#调用FireDetect.work类
        self.ccd.setDaemon(True)
        self.ccd.start()#启动线程
        self.video_path = ''

        self.btnOpenCam.setEnabled(False)
        self.btnOpenVideo.setEnabled(False)
        self.btnImgTest.setEnabled(False)
        self.btnClose.setEnabled(True)
        self.btnQuit.setEnabled(False)

    # 视频文件火焰检测                  
    def OpenVideo(self):
        print("视频文件火焰检测")
        self.flag = 0
        self.video_flag = 2
        #self.video_path = "./1.avi"
        path,_ =QFileDialog.getOpenFileName(self,'OpenFile',
                                "./","Video files (*.mp4 *.avi)")

        if path == "":
            return
        
        self.video_path = path

        #开启火焰检测线程
        self.ccd=FireDetect.Work(self)
        self.ccd.setDaemon(True)
        self.ccd.start()
        

        self.btnOpenCam.setEnabled(False)
        self.btnOpenVideo.setEnabled(False)
        self.btnImgTest.setEnabled(False)
        self.btnClose.setEnabled(True)
        self.btnQuit.setEnabled(False)

    def ImgTest(self):
        path,_ =QFileDialog.getOpenFileName(self,'OpenFile',"./",
                                             "Image files (*.jpg *.bmp *.png)")
        img = cv2.imread(path)
        if img is None:
            print("Open Image Failed!")
            return

        WorkClass=FireDetect.Work(self)
        WorkClass.img_detect(img)

    def CloseTest(self):
        self.flag = 1
        self.btnOpenCam.setEnabled(True)
        self.btnOpenVideo.setEnabled(True)
        self.btnImgTest.setEnabled(True)
        self.btnClose.setEnabled(False)
        self.btnQuit.setEnabled(True)
         
    def closeSlot(self):
        #self.number.setText("")
        self.label.clear()
        #self.label2.clear()
        self.detect_flag = 0
        self.timer_camera.stop()
        self.cap.release()
        #self.btnOpen.setEnabled(True)
        self.btnClose.setEnabled(False)
        self.btnQuit.setEnabled(True)
    
   
    

if __name__ == '__main__':
    a = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.setWindowTitle('OpenCV火焰检测系统')
    sys.exit(a.exec_())

