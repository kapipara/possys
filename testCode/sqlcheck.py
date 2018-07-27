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
            # NFCIDテーブルから条件付き全件取得
            # executeで実行コマンドを指定，fetchallで一致データすべてを取得
            self.cursor.execute("SELECT * FROM NFCID WHERE IDm='%s'"%IDm)   # 関数内はSQL文
            serverData = self.cursor.fetchall()  # 取得データ代入
            for i in serverData:
                if IDm in i:
                    return True
                else:
                    return False
        finally:
            self.cursor.close()
            self.db.close()
            print("[ERROR] Database Connection ERROR!\n")
            return False
    
    # ユーザ追加
    def addUser(self):
        cond = True
        try:
            while cond:
                print("新規ユーザー登録を行います。\n")
                print("UserName:")
                name = input(">> ")
                print("EmailAddress:")
                mail = input(">> ")
                print("Your input data:\n")
                print("UserName:" + name)
                print("EmailAddress:" + mail)
                print("Confirm? [y/n](nothing default, only [y/n])")
                confirm = None
                confirm = input(">> ")
                cond = False
                if(confirm == 'n'):
                    cond = True
                elif(confirm == 'y'):
                    break
                else:
                    print("Plz only input y/n or Nothing!!!\n")
                    cond = True
                
            # MemberListテーブルからMemberNum最大値取得
            # SQL文の意味は，「MemberNumのデータが欲しい，MemberListから，次の条件に一致するもの → (MemberNumが，MemberNumカラムの中で最大値のとき，そのカラムはMemberListにあるよ)」
            self.cursor.execute("SELECT MemberNum FROM MemberList WHERE MemberNum=(SELECT MAX(MemberNum) FROM MemberList)")  # 関数内はSQL文
            newMemberNum = self.cursor.fetchall() + 1  # 取得データ代入
            
            # 新規ユーザデータをデータベースへ入力
            self.cursor.execute("INSERT INTO MemberList (MemberNum, Name, Email, wallet) VALUES ('%d','%s','%s',0)"%(newMemberNum, name, mail)) # 関数内はSQL文 変数はタブタプ
            self.cursor.commit()    # SQL文をデータベースへ送信(返り血はないのでcommitメソッド)

        finally:
            self.cursor.close()
            self.db.close()
            print("[ERROR] Database Connection ERROR!\n")
            return False
        
temp = Database()
print(temp.checkIDm("114514ABCDEF1919"))
temp.addUser()
