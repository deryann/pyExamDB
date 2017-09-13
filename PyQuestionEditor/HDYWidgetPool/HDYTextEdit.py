#coding=utf-8
# -*- coding: utf-8 -*-
import sys, os, re, codecs
import difflib
import sys, os, re, codecs
import difflib
from PyQt4.Qt import Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, SIGNAL

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from QDbReport.toollib import getJiebaCutList

class HDYTextEdit(QTextEdit):
    def __init__(self, *args):
        QTextEdit.__init__(self,*args)
        self.dicKeyWordMapColor={}
        self.dicColorMapKeyWordList={}
#        self.dicKeyWordMapColor={u"平":Qt.yellow} #Test Function
#        self.dicColorMapKeyWordList = {Qt.blue:[u'三',u'形']} #Test Function
        self.setFont(QFont("Consolas", 14))  # 設定字型

    def setDicKeyWordMappingColor(self, dicInput):
        self.dicKeyWordMapColor = dicInput

    def setColorMappingKeyWordList(self, dicInput):
        self.dicColorMapKeyWordList = dicInput

    def setText(self, qstr):
        '''
        除了原始設定的setTextFunction 以外
        另外將所有的 Keyword 上色
        :param qstr:
        :return:
        '''
        QTextEdit.setText(self, qstr)
        for key in self.dicKeyWordMapColor.keys():
            fmt = QTextCharFormat()
            fmt.setBackground(self.dicKeyWordMapColor[key])
            doc = self.document()
            curCursor = QTextCursor(doc)
            while True:
                cursor = doc.find(key, curCursor)
                if cursor.isNull():
                    break
                cursor.setCharFormat(fmt)
                curCursor=cursor

        for key in self.dicColorMapKeyWordList.keys():
            cr = key
            lst = self.dicColorMapKeyWordList[cr]
            for keyword in lst:
                fmt = QTextCharFormat()
                fmt.setBackground(cr)
                doc = self.document()
                curCursor = QTextCursor(doc)
                while True:
                    cursor = doc.find(keyword, curCursor)
                    if cursor.isNull():
                        break
                    cursor.setCharFormat(fmt)
                    curCursor = cursor
        #比較Jieba 的結果
        lstString = getJiebaCutList(qstr)
        self.append(os.linesep)
        self.append(u"==========================================")
        self.append(os.linesep)
        fm = self.currentCharFormat()

        for item in lstString:
            lst = self.dicColorMapKeyWordList[Qt.yellow]
            self.moveCursor(QTextCursor.End)
            curCursor = self.textCursor()
            if item in lst:
                doc = self.document()
                fmt = QTextCharFormat()
                fmt.setBackground(Qt.yellow)
                curCursor.insertText(item, fmt)
            else:
                curCursor.insertText(item, fm)


