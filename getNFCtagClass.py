#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import nfc 

class getNFCtag():
    def __init__(self):
         pass

    def on_connect(self,tag):
        tmp = str(tag)
        self.splitOut = tmp.replace('=',' ').split()

        flag = 0

        for item in self.splitOut:
            if flag == 1:
                print(item)
                flag = 0
            if item.find("ID") is not -1:
                flag = 1
    
    def on_startup(self,tag):
        print("[NFC reader] : ready")
        return tag

    def main(self):
        with nfc.ContactlessFrontend('usb:054c:06c3') as self.clf:
            self.clf.connect(rdwr = {
                'on-startup':self.on_startup,
                'on-connect':self.on_connect
            })

getNFCtag = getNFCtag()
getNFCtag.main()
