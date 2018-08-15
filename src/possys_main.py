#! /usr/bin/python
#! -*- coding:utf-8 -*-
# Python3で動くよ！

##################################################################
# POS-System for ProconRoom                             Ver2.10  #
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
# ユーザーパスワードのハッシュ用
import hashlib
import getpass
# Slack接続用
import slackweb

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

        # Slack接続クラスのインスタンスを作成
        self.slack = slackLink()

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

    # ユーザが存在するか確認する
    def checkUser(self,name):
        print("[START ]: checkUser...")
        self.cursor.execute("SELECT * FROM MemberList WHERE Name='%s'"%str(name))
        getUser = self.cursor.fetchall()
        if not getUser:
            return False
        return True
        print("[  OK  ]: user exists")

    # ユーザ追加
    def addUser(self,name,mail,hashcode):
        try:
            print("[START ]: add User...")
                
            # MemberListテーブルからMemberNum最大値取得
            # SQL文の意味は，「MemberNumのデータが欲しい，MemberListから，次の条件に一致するもの → (MemberNumが，MemberNumカラムの中で最大値のとき，そのカラムはMemberListにあるよ)」
            self.cursor.execute("SELECT MemberNum FROM MemberList WHERE MemberNum=(SELECT MAX(MemberNum) FROM MemberList)")  # 関数内はSQL文
            newMemberNum = self.cursor.fetchall()  # 取得データ代入
            newMemberNum = newMemberNum[0][0] + 1
            print("[  OK  ]: Got latest userNumber")
          
            # 新規ユーザデータをデータベースへ入力
            self.cursor.execute("INSERT INTO MemberList (MemberNum, Name, Email, PASSWORD, wallet) VALUES ('%d','%s','%s','%s',0)"%(newMemberNum, name, mail, str(hashcode))) # 関数内はSQL文 変数はタブタプ
            self.db.commit()    # SQL文をデータベースへ送信(返り血はないのでcommitメソッド)
            print("[  OK  ]: Add new user")

            # ログ送信
            self.slack.post(2,self.getUserLog())

        except:
            self.cursor.close()
            self.db.close()
            print("[ERROR ]: Function addUser internal ERROR!")
            print("[ERROR ]: Database Connection ERROR!")
            return

    # NFCカード追加処理
    def addCard(self,userIDm,userName,hashcode):
        try:
            print("[START ]: add new NFC card...")
            
            # NFCIDテーブルからDataNum最大値取得
            self.cursor.execute("SELECT DataNum FROM NFCID WHERE DataNum=(SELECT MAX(DataNum) FROM NFCID)")  # 関数内はSQL文
            newDataNum = self.cursor.fetchall()  # 取得データ代入
            newDataNum = newDataNum[0][0] + 1
            print("[  OK  ]: Got latest dataNumber")

            # MemberListテーブルから指定ユーザー名のユーザー番号を取得
            try:
                self.cursor.execute("SELECT MemberNum FROM MemberList WHERE Name='%s'"%userName)
                userNum = self.cursor.fetchall()    # 取得データ代入
                userNum = userNum[0][0]
                print("[  OK  ]: Got user number")
            except:
                print("ユーザー名が異なっているか，未登録です。ご確認の上，再度お試しください。")
                raise

            # MemberListテーブルから指定ユーザー名のハッシュフレーズを取得
            try:
                self.cursor.execute("SELECT PASSWORD FROM MemberList WHERE PASSWORD='%s'"%str(hashcode))
                serverHash = self.cursor.fetchall()     # 取得データ代入
                if hashcode != serverHash[0][0]:
                    raise
                print("[  OK  ]: Got server passphrase")
            except:
                print("パスワードが間違っています。ご確認の上，再度お試しください。")
                raise

            # カードを追加
            self.cursor.execute("INSERT INTO NFCID (DataNum, MemberNum, IDm) VALUES ('%d','%d','%s')"%(int(newDataNum),int(userNum),userIDm))
            self.db.commit()    # SQL文をデータベースへ送信(返り血はないのでcommitメソッド)
            print("[  OK  ]: Add new user card")

            # ログ送信
            self.slack.post(3,self.getNFCLog())

        except:
           self.cursor.close()
           self.db.close()
           print("[ERROR ]: Function addCard internal ERROR!")
           print("[ERROR ]: Database Connection ERROR!")
           print("ユーザー名が異なっているか，未登録です。ご確認の上再度お試しください。")
           return 

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

            # ログ送信
            self.slack.post(1,self.getMoneyLog())


        except:
            self.cursor.close()
            self.db.close()
            print("[ERROR ]: Function money internal ERROR!")
            print("[ERROR ]: Database Connection ERROR!")
            return False
    
    # 残高表示
    def checkWallet(self,IDm):
        print("[START ]: Getting your wallet value...")

        # IDmからユーザ番号を取得
        userNum = self.checkIDm_userNum(IDm)

        # ユーザ番号の該当者の残高を取得
        self.cursor.execute("SELECT wallet FROM MemberList WHERE MemberNum=%d"%userNum)
        print("[  OK  ]: Got wallet data")
        wallet = self.cursor.fetchall()
        wallet = int(wallet[0][0])
        return wallet
    
    # 決済ログ取得
    def getMoneyLog(self):
        print("[START ]: Getting money log data...")

        # ユーザー名付きでログ情報取得
        # メンバー番号，メンバー名，決済時タイムスタンプ，決済額を取得(リスト型で返される)
        self.cursor.execute("SELECT MemberList.MemberNum, MemberList.Name, MoneyLog.Date, MoneyLog.Money FROM MemberList, MoneyLog WHERE MoneyLog.MemberNum=MemberList.MemberNum AND MoneyLog.LogNum=(SELECT MAX(LogNum) FROM MoneyLog)")
        logData = self.cursor.fetchall()
        print("[  OK  ]: Got money log")

        return logData
    
    # ユーザーログ取得
    def getUserLog(self):
        print("[START ]: Getting user log data...")

        # ユーザーの追加情報を取得
        # ユーザー番号，メンバー名を取得
        self.cursor.execute("SELECT MemberNum,Name FROM MemberList WHERE MemberNum=(SELECT MAX(MemberNum) FROM MemberList)")
        logData = self.cursor.fetchall()
        print("[  OK  ]: Got user log")

        return logData
    
    # NFCカード追加ログ取得
    def getNFCLog(self):
        print("[START ]: Getting NFC log data...")

        # NFCカードの追加情報を取得
        # ユーザー番号，ユーザー名，カード番号を取得
        self.cursor.execute("SELECT MemberList.MemberNum, MemberList.Name, NFCID.DataNum FROM MemberList, NFCID WHERE MemberList.MemberNum=NFCID.MemberNum AND NFCID.DataNum=(SELECT MAX(NFCID.DataNum) FROM NFCID) ")
        logData = self.cursor.fetchall()
        print("[  OK  ]: Got NFC log")

        return logData

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
        # configファイルを参照
        config = configparser.SafeConfigParser()
        config.read('setting.ini')

        # Slackのpossys_logチャンネルに接続
        self.slack = slackweb.Slack(url=config.get('SLACK','url'))

    def post(self, mode, logData):
        # 金銭ログの場合
        if mode == 1:
            self.slack.notify(text=("[決済] : [%d]%s さんが [%s] に %d 円決済しました。")%(int(logData[0][0]), str(logData[0][1]), str(logData[0][2]), int(logData[0][3])))
        
        # ユーザーログの場合
        elif mode == 2:
            self.slack.notify(text=("[ユーザー追加] : ユーザー番号[%d]に %s さんが登録されました。")%(int(logData[0][0]), str(logData[0][1])))
        
        # NFCカード追加ログの場合
        elif mode == 3:
            self.slack.notify(text=("[カード追加] : [%d]%s さんに カード番号[%d] の　NFCカードを追加しました。")%(int(logData[0][0]), str(logData[0][1]), int(logData[0][2])))
        
        # それ以外
        else:
            pass

class mainMenu:
    def __init__(self):
        self.database = Database()
        self.idmRead = idmRead()
    
    def mainLogic(self):
        while True:
            print("***** Welcom to possys ! *****")
            print("Made by kapipara 2018/08/03 released ver2.1")
            print("1.購入")
            print("2.入金")
            print("3.残高照会")
            print("4.ユーザー登録")
            print("5.NFCカード登録")
            print("6.NFCカード消去")
            print("7.ユーザー消去")
            print("select mode:")
            mode = input(">> ")

            # 購入モード
            if mode == '1':
                print("購入金額を入力してください...")
                amount = str(input(">> "))
                if not amount.isdigit:
                    print("[WARNING]: 適切な数値を入力してください。3億円以上はサポートしていません。")
                    break
                print("登録済みのNFCカードをタッチしてください。")
                amount = -int(amount)
                tag = self.idmRead.getMain()
                userNum = self.database.checkIDm_userNum(tag)
                self.database.money(userNum, amount)
                print("ご購入ありがとうございました。またのご利用をお待ちしております。")

            # 入金モード
            elif mode == '2':
                print("※※※ 必ず貯金箱に現金を投入してから処理を行ってください！ ※※※")
                print("入金金額を入力してください...")
                amount = str(input(">> "))
                if not amount.isdigit:
                    print("[WARNING]: 適切な数値を入力してください。3億円以上はサポートしていません。")
                    break
                print("登録済みのNFCカードをタッチしてください。")
                tag = self.idmRead.getMain()
                userNum = self.database.checkIDm_userNum(tag)
                self.database.money(userNum, amount)
                print("\nご入金ありがとうございます。データベースが更新されました。") 

            # 残高照会モード
            elif mode == '3':
                print("残高照会を行います。")
                print("NFCカードを置いてください。")
                tag = self.idmRead.getMain()
                wallet = self.database.checkWallet(tag)
                print("\nあなたの残高は %d 円です。"%wallet)
                if wallet < 0:
                    print("※※※ あなたは借金しています。 ※※※")
                    print("会計から任意のタイミングで徴収されても，返金できる額にとどめてください。")

            # ユーザー登録モード
            elif mode == '4':
                print("ようこそ possys へ！")
                print("ユーザー登録を行います。必要事項を入力してください。\n")
                print("パスワードは入力後にSHA256でハッシュされ，データベースに送信されます。\n")
                cond = True
                passcond = True
                while cond:
                    print("UserName:")
                    name = input(">> ")
                    print("EmailAddress:")
                    mail = input(">> ")
                    # パスワードのハッシュ処理
                    while passcond:
                        hashman1 = hashlib.sha256()
                        hashman2 = hashlib.sha256()
                        hashman1.update(getpass.getpass().encode('utf-8'))
                        hash1 = hashman1.hexdigest()
                        hashman2.update(getpass.getpass("Password (Plese agein):").encode('utf-8'))
                        hash2 = hashman2.hexdigest()
                        passcond = False
                        if hash1 != hash2:
                            print("入力されたパスワードが一致しません。もう一度入力してください。")
                            passcond = True
                    print("\nあなたが入力したデータは以下の通りです。")
                    print("UserName : " + name)
                    print("EmailAddress : " + mail)
                    print("Password : ハッシュされたため表示しません。")
                    print("\nよろしいですか？ [y/n]\n(nothing default, only [y/n])")
                    confirm = None
                    confirm = input(">> ")
                    cond = False
                    if(confirm == 'n'):
                        cond = True
                        passcond = True
                    elif(confirm == 'y'):
                        break
                    else:
                        print("Plz only input y/n or Nothing!!!\n")
                        cond = True
                self.database.addUser(name,mail,hash1)
                print("\nご登録ありがとうございます。続いてカード登録を行ってください。")
            
            # NFCカード追加モード
            elif mode == '5':
                hashman = hashlib.sha256()
                print("新規カード登録処理を行います。")
                print("あなたのユーザー名を入力してください。")
                userName = input(">> ")
                if not self.database.checkUser(str(userName)):
                    print("存在しないユーザです。")
                    break
                print("あなたのパスワードを入力してください。")
                hashman.update(getpass.getpass().encode('utf-8'))
                hashcode = hashman.hexdigest()
                print("続いて，追加したいカードをタッチしてください。")
                tag = self.idmRead.getMain()
                self.database.addCard(tag,userName,hashcode)
                print("\nカードのご登録を承りました。只今より当該カードはご利用いただけます。")

            # NFCカード消去モード
            elif mode == '6':
                print("当機能は未実装です。管理者へ問い合わせてください。")

            # ユーザー消去モード
            elif mode == '7':    
                print("当機能は未実装です。管理者へ問い合わせてください。")

            # 変な値を入力されたとき
            else:
                print("1~7までの数値を入力してください。")
            
            print("\n")

#try:
temp = mainMenu()
temp.mainLogic()
#except:
    #print("[ERROR ]: Serious ERROR!!")
