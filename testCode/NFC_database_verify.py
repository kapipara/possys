#! /usr/bin/python
#! -*- coding:utf-8 -*-
# Python3で動くよ！

# configファイル
import configparser
# 時間取得用
import time
# データベースアクセス
import mysql.connector
# IDm取得用のライブラリ(Python2をサブプロセスで実行)
import subprocess
import os
import sys

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
        print("[  OK  ]: Establish database connection")

    # IDm照合処理
    def checkIDm(self, userIDm):
        try:
            print("[START ]: check NFC IDm...")
            # NFCIDテーブルから条件付き全件取得
            # executeで実行コマンドを指定，fetchallで一致データすべてを取得
            self.cursor.execute("SELECT IDm  FROM NFCID WHERE IDm='%s'"%str(userIDm))   # 関数内はSQL文
            serverData = self.cursor.fetchall()  # 取得データ代入
            print("[  OK  ]: Got server side IDm data")
            # 重複データがあっても，[0][0]にはとりあえず取得データがある
            # ない場合，list型の範囲外参照エラーが起きるのでexceptで拾ってあげる
            try:
                if str(serverData[0][0]) == str(userIDm):
                    return True
            except:
                return False

        except:
            self.cursor.close()
            self.db.close()
            print("[ERROR ]: Database Connection ERROR!")
            return False
            
    # ユーザ追加
    def addUser(self):
        try:
            cond = True
            print("[START ]: add User...")
            while cond:
                print("\n新規ユーザー登録を行います。")
                print("UserName:")
                name = input(">> ")
                print("EmailAddress:")
                mail = input(">> ")
                print("\nYour input data:")
                print("UserName:" + name)
                print("EmailAddress:" + mail)
                print("\nConfirm? [y/n]\n(nothing default, only [y/n])")
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
            newMemberNum = self.cursor.fetchall()  # 取得データ代入
            newMemberNum = newMemberNum[0][0] + 1
            print(newMemberNum)
            print("[  OK  ]: Got most new MemberNum")
            # 新規ユーザデータをデータベースへ入力
            self.cursor.execute("INSERT INTO MemberList (MemberNum, Name, Email, wallet) VALUES ('%d','%s','%s',0)"%(newMemberNum, name, mail)) # 関数内はSQL文 変数はタブタプ
            self.db.commit()    # SQL文をデータベースへ送信(返り血はないのでcommitメソッド)
            print("[  OK  ]: Add new user")

        except:
            self.cursor.close()
            self.db.close()
            print("[ERROR ]: Database Connection ERROR!")
            return False

class idmRead:
    def __init__(self):
        pass
    
    def getMain(self):
        print("[START ]: Getting NFC card IDm...")
        command = "python2 idmRead.py"      # 同一ディレクトリ内のidm取得プログラムをpython2で実行
        # サブシステムでcommandを実行，stringに変換してスペースでスプリット
        output = str(subprocess.check_output(command.split()))
        temp = output.split()
        flag = 0
        for tag in temp:
            if flag == 1:
                # 「hogehoge\n'」と取得できるので，後ろから3字消去
                tag = tag[:-3]
                flag = 0
                print("[  OK  ]: Got IDm")
                return(tag)
            # 「IDm」の後にスペースを置いてIDmが来るようにしてあるので，フラグ付けて次ループで回収
            if tag.find("IDm=") is not -1:
                flag = 1

temp = Database()
temp2 = idmRead()
test = temp2.getMain()
print(temp.checkIDm(test))