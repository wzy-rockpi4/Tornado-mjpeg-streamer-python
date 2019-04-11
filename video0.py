#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np


class UsbCamera(object):
    __gst__ = "gst-launch-1.0 " \
            "rkcamsrc device=/dev/video0 io-mode=4 isp-mode=0A !  " \
            "video/x-raw,format=NV12,framerate=15/1,width=800,height=600 !  " \
            "videomixer name=mix ! " \
            "videoconvert ! video/x-raw,format=I420,width=800,height=600 ! " \
            "queue ! " \
            "appsink sync=false " \
            "videotestsrc background-color=0x000000 pattern=black !  " \
            "video/x-raw, framerate=10/1, width=800, height=80 !  " \
            "timeoverlay font-desc=\"Sans 18\"  text= \"字幕\" halignment=center ! capsfilter caps=\"video/x-raw\" ! " \
            "mix."

    __gst2__ = "gst-launch-1.0 "\
            "rkcamsrc device=/dev/video0 io-mode=4 isp-mode=0A ! "\
            "video/x-raw,format=NV12,width=800, height=600 ! "\
            "timeoverlay font-desc=\"Sans 28\" text=\"字幕\" ! "\
            "capsfilter caps=\"video/x-raw\" ! "\
            "videoconvert ! "\
            "appsink sync=false "

    __gst3__ = "gst-launch-1.0 " \
            "videomixer name=mix ! appsink sync=false "\
            "rkcamsrc device=/dev/video0 io-mode=4 isp-mode=0A !  " \
            "video/x-raw,format=NV12,framerate=15/1,width=800,height=600 !  " \
            "videoconvert ! video/x-raw,format=I420,width=800,height=600 ! " \
            "queue ! "\
            "mix. "\
            "videotestsrc background-color=0x000000 pattern=black !  " \
            "video/x-raw, framerate=10/1, width=800, height=80 !  " \
            "timeoverlay font-desc=\"Sans 18\"  text= \"字幕\" halignment=center ! capsfilter caps=\"video/x-raw\" ! " \
            "queue ! "\
            "mix."

    """ Init camera """
    def __init__(self):
        # select first video device in system
        #self.cam = cv2.VideoCapture(0)
        # set camera resolution
        self.w = 800
        self.h = 600
        
        gst = self.__gst2__
        print("> " + gst)
        self.cam = cv2.VideoCapture(gst)
        ## set crop factor
        #self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
        #self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        # load cascade file

        #self.cam.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('N','V','1','2'))
        #print("{0}".format(self.cam.get(cv2.CAP_PROP_FOURCC)))
        self.face_cascade = cv2.CascadeClassifier('face.xml')

    def set_resolution(self, new_w, new_h):
        """
        functionality: Change camera resolution
        inputs: new_w, new_h - with and height of picture, must be int
        returns: None ore raise exception
        """
        if isinstance(new_h, int) and isinstance(new_w, int):
            # check if args are int and correct
            if (new_w <= 800) and (new_h <= 600) and \
               (new_w > 0) and (new_h > 0):
                self.h = new_h
                self.w = new_w
            else:
                # bad params
                raise Exception('Bad resolution')
        else:
            # bad params
            raise Exception('Not int value')

    def get_frame(self, fdenable):
        """
        functionality: Gets frame from camera and try to find feces on it
        :return: byte array of jpeg encoded camera frame
        """
        success, image = self.cam.read()
        if success:
            # scale image
            image = cv2.resize(image, (self.w, self.h))
            if fdenable:
                # resize image for speeding up recognize
                gray = cv2.resize(image, (320, 240))
                # make it grayscale
                gray = cv2.cvtColor(gray, cv2.COLOR_YUV2GRAY_NV12)
                # face cascade detector
                faces = self.face_cascade.detectMultiScale(gray)
                # draw rect on face arias
                scale = float(self.w / 320.0)
                count = 0
                for f in faces:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    x, y, z, t = [int(float(v) * scale) for v in f]
                    cv2.putText(image, str(x) + ' ' + str(y), (0, (self.h - 10 - 25 * count)), font, 1, (0, 0, 0), 2)
                    count += 1
                    cv2.rectangle(image, (x, y), (x + z, y + t), (255, 255, 255), 2)
        else:
            image = np.zeros((self.h, self.w, 3), np.uint8)
            cv2.putText(image, 'No camera', (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        # encoding picture to jpeg
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()
