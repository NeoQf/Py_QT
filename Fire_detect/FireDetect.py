# -*- coding: cp936 -*-
import sys
import threading #线程模块
import cv2
import numpy as np
import time
import os
import sys
from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap,QFont,QIcon
from PyQt5.QtWidgets import (QApplication,QDialog, QFileDialog, QGridLayout,
                QLabel, QPushButton,QHBoxLayout,QFrame,QWidget,QLineEdit)

 

font = cv2.FONT_HERSHEY_SIMPLEX #设置字体
 
class Work(threading.Thread):
    def __init__(self, caller):
        threading.Thread.__init__(self)
        self.caller = caller #父类调用者
        self.isHaveFire = False #全局变量是否检测到火焰
        
    def run(self): #线程启动后自动调用此函数
        cap = cv2.VideoCapture()#初始化VideoCapture类对象
        if(self.caller.video_flag == 1):#标志位为1，对应打开摄像头
            cap = cv2.VideoCapture(0)  #打开摄像头
            print("打开摄像头")
        else: #标志位为1，对应打开视频文件
            cap = cv2.VideoCapture(self.caller.video_path)#打开对应路径的视频文件
            print("打开视频文件%s"%self.caller.video_path)
        while(1):
            if(self.caller.flag): #如果视频结束标志位为1，则退出并清空图像
                bgImg = np.ones((640,480,3),np.uint8)*240
                self.showViewImg(self.caller.label, bgImg) 
                break
            ret, frame = cap.read() #读取视频或摄像头帧
            if(ret==False):#取帧失败，提示退出循环
                print("摄像头打开失败！" )
                break
            time.sleep(0.001)
            frame = self.fire_detect(frame)#调用火焰检测函数
            
            frameTest = frame.copy()#原图备份
            self.showViewImg(self.caller.label, frame)
            
        cap.release()#释放VideoCapture类对象

    def showViewImg(self,label,img):
        # 提取图像的尺寸和通道, 用于将opencv下的image转换成Qimage
        #self.label.clear()
        channel = 1
        height = width = 1
        try:
            height, width, channel = img.shape
        except:
            channel = 1
        showImg = None
        if channel != 3:
            showImg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
        else:
            showImg = img.copy()
        
        bytesPerLine = 3 * width 
        qImg = QImage(showImg.data, width, height, bytesPerLine,
                           QImage.Format_RGB888).rgbSwapped()

        # 将Qimage显示出来
        label.setPixmap(QPixmap.fromImage(qImg))
        
    def img_detect(self,img):#加载图片检测火焰
        print("Image Test")
        frame = self.fire_detect(img)#调用检测火焰函数
        self.showViewImg(self.caller.label, frame)
        
         
    def fire_detect(self,frame): #火焰检测函数，核心算法
        self.isHaveFire = False #初始化火焰检测结果标志位False
        redThres = 49 #红色阈值
        sat = 7 #比例系数
        blackImg = np.zeros((frame.shape[0],frame.shape[1],1),np.uint8)#创建原图同大小的黑色图像
        b,g,r = cv2.split(frame)#通道分离
        for i in range(0,frame.shape[0]): #访问所有行
            for j in range(0,frame.shape[1]): #访问所有列
                B = int(b[i,j])#访问第i行，第j列蓝色像素值
                G = int(g[i,j])#访问第i行，第j列绿色像素值
                R = int(r[i,j])#访问第i行，第j列红色像素值
                maxValue = max(max(B,G),R)#求RBG像素最大值
                minValue = min(min(B,G),R)#求RBG像素最小值
                if (R+G+B) == 0:
                    break
                S = (1-3.0*minValue/(R+G+B))#计算S值
                if(R>redThres and R>=G and G>=B and S>((255-R)*sat/redThres)):#火焰像素删选
                   blackImg[i,j] = 255 #满足火焰像素，黑色图像对应位置变为白色
                else:
                   blackImg[i,j] = 0 #不满足火焰像素，黑色图像对应位置仍为黑色
        blackImg = cv2.medianBlur(blackImg,5)#中值滤波滤除小杂讯
        k1=np.ones((5,5), np.uint8)#指定膨胀核大小5*5
        blackImg = cv2.dilate(blackImg, k1, iterations=1)#膨胀
        #查找火焰部分轮廓
        contours,hierarchy = cv2.findContours(blackImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        index = -1
        maxArea = 0
        for i in range (0,len(contours)):#遍历轮廓
            (x0, y0, w0, h0) = cv2.boundingRect(contours[i])#获取轮廓外界矩形
            if(w0>10 and h0>10):#删选外界矩形宽高均大于10
                #cv2.rectangle(frame,(x0,y0),(x0+w0,y0+h0),(0,255,0),2)
                if(w0*h0>maxArea):#比对轮廓面积
                    maxArea = w0*h0 #获取最大面积
                    index = i #获取最大面积对应的轮廓序号
        if index != -1: #轮廓序号变化了说明没检测到火焰
            area = cv2.contourArea(contours[index])#获取火焰轮廓对应的面积
            cv2.putText(frame,("FireArea=%0.2f"%(area)), (5,20), font, 0.7, (0,255,0), 2)#图片上输出面积
            (x0, y0, w0, h0) = cv2.boundingRect(contours[index])#获取外界矩形
            cv2.rectangle(frame,(x0,y0),(x0+w0,y0+h0),(0,255,0),2)#绘制外界矩形框出火焰区域
            self.isHaveFire = True #检测到火焰标志位为True,对应会播放声音
            
        else: #轮廓序号没变说明没检测到火焰
            cv2.putText(frame,("FireArea=0"), (5,20), font, 0.7, (0,255,0), 2)#火焰面积为0
        return frame #返回最终处理后的图像
        

if __name__=="__main__":
    pass
