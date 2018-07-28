#!/usr/bin/env python
#! -*- coding: utf-8 -*-

# NFC周りのライブラリ(Python2系でしか使えない)
import nfc 

class getNFCtag():
    # インスタンス処理は特にいらない
    def __init__(self):
         pass

    # NFCカード接続成功時の処理
    def on_connect(self,tag):
        # String型に変換，イコールとスペースでスプリット
        tmp = str(tag)
        splitOut = tmp.replace('=',' ').split()

        flag = 0
        for item in splitOut:
            if flag == 1:
                print("[ NFC  ]: IDm= " + item )
                flag = 0
            # 「ID」の後がIDmなので，フラグを立てて次ループで回収
            if item.find("ID") is not -1:
                flag = 1
    
    # NFCリーダー接続時の処理
    def on_startup(self,tag):
        print("[ NFC  ]: Card reader ready")
        return tag

    def main(self):
        # デバイスIDが054c:06c3のUSB接続ドライバをNFCリーダーとして参照
        with nfc.ContactlessFrontend('usb:054c:06c3') as self.clf:
            self.clf.connect(rdwr = {
                'on-startup':self.on_startup,
                'on-connect':self.on_connect
            })

tag = getNFCtag()
tag.main()
