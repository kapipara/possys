#! /usr/bin/python
#! -*- coding:utf-8 -*-
# Python3で動くよ！

##################################################################
# POS-System for ProconRoom                             Ver1.00  #
# 東京工業高等専門学校 プログラミングコンテストゼミ部室用        #
# NFCカード 簡易決済システム                                     #
# <各ファイルの説明>                                             #
#     ・説明，注意，システムの著作権などはREADME.mdにあります。  #
#     ・システムの起動に必要なものはInstallList.mdにあります。   #
#     ・データベースの構成はdatabaseConstruct.mdにあります。     #
#     ・possysの諸設定はsetting.iniを所定の書式で編集してくださ  #
#       い。                                                     #
##################################################################

# configファイル
import configparser
# 時間取得用
import datetime
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
            print("[ERROR ]: Function checkIDm internal ERROR!")
            print("[ERROR ]: Database Connection ERROR!")
            return False

    # IDmからユーザを参照する処理 (↑で2変数返せば良くね？とか言わないように)
    def checkIDm_userNum(self,userIDm):
        try:
            print("[START ]: check NFC IDm and MemberNum...")
           
            # NFCIDテーブルから条件付き全件取得
            # executeで実行コマンドを指定，fetchallで一致データすべてを取得
            self.cursor.execute("SELECT MemberNum FROM NFCID WHERE IDm='%s'"%str(userIDm))   # 関数内はSQL文
            serverData = self.cursor.fetchall()  # 取得データ代入
            print("[  OK  ]: Got server side IDm data")
            
            # データがない場合，list型の範囲外参照エラーが起きるのでexceptで拾ってあげる
            try:
                # DataNum-UserNum-IDmの順なので，(n,3)にIDm，(n,2)にUserNumがある
                # 一致データがあればどこでもいいので先頭データから取得
                if (serverData[0][3]) == str(userIDm):
                    return serverData[0][2]
            except:
                return False

        except:
            self.cursor.close()
            self.db.close()
            print("[ERROR ]: Function checkIDm_userNum internal ERROR!")
            print("[ERROR ]: Database Connection ERROR!")
            return

    # ユーザ追加
    def addUser(self,name,mail):
        try:
            print("[START ]: add User...")
                
            # MemberListテーブルからMemberNum最大値取得
            # SQL文の意味は，「MemberNumのデータが欲しい，MemberListから，次の条件に一致するもの → (MemberNumが，MemberNumカラムの中で最大値のとき，そのカラムはMemberListにあるよ)」
            self.cursor.execute("SELECT MemberNum FROM MemberList WHERE MemberNum=(SELECT MAX(MemberNum) FROM MemberList)")  # 関数内はSQL文
            newMemberNum = self.cursor.fetchall()  # 取得データ代入
            newMemberNum = newMemberNum[0][0] + 1
            print("[  OK  ]: Got latest userNumber")
          
            # 新規ユーザデータをデータベースへ入力
            self.cursor.execute("INSERT INTO MemberList (MemberNum, Name, Email, wallet) VALUES ('%d','%s','%s',0)"%(newMemberNum, name, mail)) # 関数内はSQL文 変数はタブタプ
            self.db.commit()    # SQL文をデータベースへ送信(返り血はないのでcommitメソッド)
            print("[  OK  ]: Add new user")

        except:
            self.cursor.close()
            self.db.close()
            print("[ERROR ]: Function addUser internal ERROR!")
            print("[ERROR ]: Database Connection ERROR!")
            return

    # NFCカード追加処理
    def addCard(self,userIDm,userName):
        print("[START ]: add new NFC card...")

        # NFCIDテーブルからDataNum最大値取得
        self.cursor.execute("SELECT DataNum FROM NFCID WHERE DataNum=(SELECT MAX(DataNum) FROM NFCID)")  # 関数内はSQL文
        newDataNum = self.cursor.fetchall()  # 取得データ代入
        newDataNum = newDataNum[0][0] + 1
        print("[  OK  ]: Got latest dataNumber")
        
        # MemberListテーブルから指定ユーザー名のユーザー番号を取得
        self.cursor.execute("SELECT MemberNum FROM MemberList WHERE Name='%s'"%userName)
        userNum = self.cursor.fetchall()    # 取得データ代入
        print("[  OK  ]: Got user number")
        
        # カードを追加
        self.cursor.execute("INSERT INTO NFCID (DataNum, MemberNum, IDm) VALUES ('%d','%d','%s')"%(newDataNum,userNum,IDm))
        self.db.commit()    # SQL文をデータベースへ送信(返り血はないのでcommitメソッド)
        print("[  OK  ]: Add new user card")

    # 金銭処理
    def money(self,userNum,amount):
        try:
            print("[START ]: money processing...")

            # 現在時刻取得，iso8601形式に変換
            now = datetime.datetime.now().isoformat()
            print("[  OK  ]: Got current time")

            # MoneyLogテーブルからLogNum最大値取得
            self.cursor.execute("SELECT LogNum FROM MoneyLog WHERE LogNum=(SELECT MAX(LogNum) FROM MoneyLog)")  # 関数内はSQL文
            newLogNum = self.cursor.fetchall()  # 取得データ代入
            newLogNum = newLogNum[0][0] + 1

            # MemberListのユーザーのWalletの値を更新
            self.cursor.execute("SELECT Wallet FROM MemberList WHERE MemberNum=%d"%int(userNum))                            # 関数内はSQL文
            temp = self.cursor.fetchall()
            userWallet = int(temp[0][0]) + int(amount)
            self.cursor.execute("UPDATE MemberList SET Wallet=%d WHERE MemberNum=%d"%(int(userWallet),int(userNum)))        # 関数内はSQL文
            self.db.commit()    # SQL文をデータベースへ送信(返り血はないのでcommitメソッド)

            # 金銭ログをデータベースへ入力
            self.cursor.execute("INSERT INTO MoneyLog (LogNum, MemberNum, Date, Money) VALUES ('%d','%d','%s','%d')"%(int(newLogNum), int(userNum), now, int(amount))) # 関数内はSQL文
            self.db.commit()    # SQL文をデータベースへ送信(返り血はないのでcommitメソッド)
            print("[  OK  ]: Update money log")

        except:
            self.cursor.close()
            self.db.close()
            print("[ERROR ]: Function money internal ERROR!")
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
                print("[  OK  ]: Got your cards IDm")
                return(tag)
            # 「IDm」の後にスペースを置いてIDmが来るようにしてあるので，フラグ付けて次ループで回収
            if tag.find("IDm=") is not -1:
                flag = 1

class slackLink:
    def __init__(self):
        pass

class mainMenu:
    def __init__(self):
        self.database = Database()
        self.idmRead = idmRead()
    
    def mainLogic(self):
        while True:
            print("***** Welcom to possys ! *****")
            print("select mode:")
            print("1.購入")
            print("2.入金")
            print("3.ユーザー登録")
            print("4.NFCカード登録")
            print("5.NFCカード消去")
            print("6.ユーザー消去")
            mode = int(input(">> "))

            # 購入モード
            if mode == 1:
                print("購入金額を入力してください...")
                amount = input(">> ")
                if not amount.isdigit:
                    print("[WARNING]: 適切な数値を入力してください。3億円以上はサポートしていません。")
                print("登録済みのNFCカードをタッチしてください。")
                amount = -int(amount)
                tag = self.idmRead.getMain()
                userNum = self.database.checkIDm_userNum(tag)
                self.database.money(userNum, amount)
                print("ご購入ありがとうございました。またのご利用をお待ちしております。")

            # 入金モード
            elif mode == 2:
                print("※※※ 必ず貯金箱に現金を投入してから処理を行ってください！ ※※※")
                print("入金金額を入力してください...")
                amount = input(">> ")
                if not amount.isdigit:
                    print("[WARNING]: 適切な数値を入力してください。3億円以上はサポートしていません。")
                print("登録済みのNFCカードをタッチしてください。")
                tag = self.idmRead.getMain()
                userNum = self.database.checkIDm_userNum(tag)
                self.database.money(userNum, amount)
                print("ご入金ありがとうございます。データベースが更新されたので安心してください。") 

            # ユーザー登録モード
            elif mode == 3:
                print("ようこそ possys へ！")
                print("ユーザー登録を行います。必要事項を入力してください。\n")
                cond = True
                while cond:
                    print("UserName:")
                    name = input(">> ")
                    print("EmailAddress:")
                    mail = input(">> ")
                    print("\nあなたが入力したデータは以下の通りです。")
                    print("UserName:" + name)
                    print("EmailAddress:" + mail)
                    print("\nよろしいですか？ [y/n]\n(nothing default, only [y/n])")
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
                self.database.addUser(name,mail)
                print("ご登録ありがとうございます。続いてカード登録を行ってください。")
            
            # NFCカード追加モード
            elif mode == 4:
                print("新規カード登録処理を行います。")
                print("あなたのユーザー名を入力してください。")
                userName = input(">> ")
                print("続いて，追加したいカードをタッチしてください。")
                tag = self.idmRead.getMain()

                
                    
temp = mainMenu()
temp.mainLogic()
