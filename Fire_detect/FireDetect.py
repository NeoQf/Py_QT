# -*- coding: cp936 -*-
import sys
import threading #�߳�ģ��
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

 

font = cv2.FONT_HERSHEY_SIMPLEX #��������
 
class Work(threading.Thread):
    def __init__(self, caller):
        threading.Thread.__init__(self)
        self.caller = caller #���������
        self.isHaveFire = False #ȫ�ֱ����Ƿ��⵽����
        
    def run(self): #�߳��������Զ����ô˺���
        cap = cv2.VideoCapture()#��ʼ��VideoCapture�����
        if(self.caller.video_flag == 1):#��־λΪ1����Ӧ������ͷ
            cap = cv2.VideoCapture(0)  #������ͷ
            print("������ͷ")
        else: #��־λΪ1����Ӧ����Ƶ�ļ�
            cap = cv2.VideoCapture(self.caller.video_path)#�򿪶�Ӧ·������Ƶ�ļ�
            print("����Ƶ�ļ�%s"%self.caller.video_path)
        while(1):
            if(self.caller.flag): #�����Ƶ������־λΪ1�����˳������ͼ��
                bgImg = np.ones((640,480,3),np.uint8)*240
                self.showViewImg(self.caller.label, bgImg) 
                break
            ret, frame = cap.read() #��ȡ��Ƶ������ͷ֡
            if(ret==False):#ȡ֡ʧ�ܣ���ʾ�˳�ѭ��
                print("����ͷ��ʧ�ܣ�" )
                break
            time.sleep(0.001)
            frame = self.fire_detect(frame)#���û����⺯��
            
            frameTest = frame.copy()#ԭͼ����
            self.showViewImg(self.caller.label, frame)
            
        cap.release()#�ͷ�VideoCapture�����

    def showViewImg(self,label,img):
        # ��ȡͼ��ĳߴ��ͨ��, ���ڽ�opencv�µ�imageת����Qimage
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

        # ��Qimage��ʾ����
        label.setPixmap(QPixmap.fromImage(qImg))
        
    def img_detect(self,img):#����ͼƬ������
        print("Image Test")
        frame = self.fire_detect(img)#���ü����溯��
        self.showViewImg(self.caller.label, frame)
        
         
    def fire_detect(self,frame): #�����⺯���������㷨
        self.isHaveFire = False #��ʼ������������־λFalse
        redThres = 49 #��ɫ��ֵ
        sat = 7 #����ϵ��
        blackImg = np.zeros((frame.shape[0],frame.shape[1],1),np.uint8)#����ԭͼͬ��С�ĺ�ɫͼ��
        b,g,r = cv2.split(frame)#ͨ������
        for i in range(0,frame.shape[0]): #����������
            for j in range(0,frame.shape[1]): #����������
                B = int(b[i,j])#���ʵ�i�У���j����ɫ����ֵ
                G = int(g[i,j])#���ʵ�i�У���j����ɫ����ֵ
                R = int(r[i,j])#���ʵ�i�У���j�к�ɫ����ֵ
                maxValue = max(max(B,G),R)#��RBG�������ֵ
                minValue = min(min(B,G),R)#��RBG������Сֵ
                if (R+G+B) == 0:
                    break
                S = (1-3.0*minValue/(R+G+B))#����Sֵ
                if(R>redThres and R>=G and G>=B and S>((255-R)*sat/redThres)):#��������ɾѡ
                   blackImg[i,j] = 255 #����������أ���ɫͼ���Ӧλ�ñ�Ϊ��ɫ
                else:
                   blackImg[i,j] = 0 #������������أ���ɫͼ���Ӧλ����Ϊ��ɫ
        blackImg = cv2.medianBlur(blackImg,5)#��ֵ�˲��˳�С��Ѷ
        k1=np.ones((5,5), np.uint8)#ָ�����ͺ˴�С5*5
        blackImg = cv2.dilate(blackImg, k1, iterations=1)#����
        #���һ��沿������
        contours,hierarchy = cv2.findContours(blackImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        index = -1
        maxArea = 0
        for i in range (0,len(contours)):#��������
            (x0, y0, w0, h0) = cv2.boundingRect(contours[i])#��ȡ����������
            if(w0>10 and h0>10):#ɾѡ�����ο�߾�����10
                #cv2.rectangle(frame,(x0,y0),(x0+w0,y0+h0),(0,255,0),2)
                if(w0*h0>maxArea):#�ȶ��������
                    maxArea = w0*h0 #��ȡ������
                    index = i #��ȡ��������Ӧ���������
        if index != -1: #������ű仯��˵��û��⵽����
            area = cv2.contourArea(contours[index])#��ȡ����������Ӧ�����
            cv2.putText(frame,("FireArea=%0.2f"%(area)), (5,20), font, 0.7, (0,255,0), 2)#ͼƬ��������
            (x0, y0, w0, h0) = cv2.boundingRect(contours[index])#��ȡ������
            cv2.rectangle(frame,(x0,y0),(x0+w0,y0+h0),(0,255,0),2)#���������ο����������
            self.isHaveFire = True #��⵽�����־λΪTrue,��Ӧ�Ქ������
            
        else: #�������û��˵��û��⵽����
            cv2.putText(frame,("FireArea=0"), (5,20), font, 0.7, (0,255,0), 2)#�������Ϊ0
        return frame #�������մ�����ͼ��
        

if __name__=="__main__":
    pass
