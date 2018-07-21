#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import pymysql.cursors
import datetime
import time

connection = pymysql.connect(host="localhost", user="possys_logic", password="pospos", db="kapi",charset="utf8m64")

now = datetime.datetime.now()

try:
    with connection.cursors() as cursor:
        sql = "insert into kapi"