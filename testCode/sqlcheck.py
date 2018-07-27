#! /usr/bin/python
#! -*- coding:utf-8 -*-
# Python3で動くよ！

# configファイル
import configparser
# 時間取得用
import time
# データベースアクセス
import mysql.connector

# データベース操作クラス
class Database:
    def __init__(self):
        # configファイルを参照
        config = configparser.SafeConfigParser()
        config.read('setting.ini')

        # データベースを参照
        # 各値はconfigファイルのDATABASEセクションから取得
        self.db = mysql.connector.connect(host     = config.get('DATABASE','hostname'),
                                               user     = config.get('DATABASE','username'),
                                               password = config.get('DATABASE','password'),
                                               database = config.get('DATABASE','databaseName')
                                              )
        # データベースとの，対話クラスのインスタンスを作成
        self.cursor = self.db.cursor()

    # IDm照合処理
    def checkIDm(self, IDm):
        try:
            # NFCIDテーブルを全件取得
            # executeで実行コマンドを指定，fetchallで一致データすべてを取得
            self.cursor.execute("SELECT * FROM NFCID WHERE IDm='%s'"%IDm)
            serverData = self.cursor.fetchall()  # 取得データ代入
            if IDm in serverData:
                return True
            else:
                return False
        finally:
            self.cursor.close()
            self.db.close()
    
    # IDm追加処理
    def addIDm(self, IDm, jobNum):
        try:

temp = Database()
print(temp.checkIDm("114514ABCDEF1919"))
