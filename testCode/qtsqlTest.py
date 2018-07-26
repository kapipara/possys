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
        self.config = configparser.SafeConfigParser()
        self.config.read('setting.ini')

        # データベースを参照
        # 各値はconfigファイルのDATABASEセクションから取得
        self.db = mysql.connector.connect(host     = config.get('DATABASE','hostname'),
                                          user     = config.get('DATABASE','username'),
                                          password = config.get('DATABASE','password'),
                                          database = config.get('DATABASE','databaseName')
                                         )
        # データベース対話クラスのインスタンスを作成
        cursor = db.cursor()


    def __open(self):
        # データベースが開けなかったときの回避処理
        if not self.db.open():
            print("[ERROR] Database can't open!\n")
            exit()

    def checkIDm(self, IDm):
        self.__open()
        query = QtSql.QSqlQuery()
        query.prepare('SELECT * FROM NFCID WHERE IDm=')
