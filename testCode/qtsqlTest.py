#! /usr/bin/python
#! -*- coding:utf-8 -*-

import ConfigParser
import time
from PyQt4 import QtSql

class Database:
    def __init__(self):
        self.config = configparser.SafeConfigParser()
        self.config.read('POSSYS_PATH')
        self.db = QtSql.QSqlDatabase.addDatabase('QMYSQL')
        self.db.setHostName