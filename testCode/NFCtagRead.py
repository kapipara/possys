#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import nfc 

def on_connect(tag):
    print tag
    tmp = str(tag)
    splitOut = tmp.replace('=',' ').split()
    
    flag = 0

    for item in splitOut:
        if flag == 1:
            print(item)
            flag = 0
        if item.find("ID") is not -1:
            flag = 1

def on_startup(tag):
    print("[NFC reader] : ready")
    return tag

def main():
    with nfc.ContactlessFrontend('usb') as clf:
        clf.connect(rdwr = {
            'on-startup':on_startup,
            'on-connect':on_connect
            })

if __name__ == '__main__':
    main()

