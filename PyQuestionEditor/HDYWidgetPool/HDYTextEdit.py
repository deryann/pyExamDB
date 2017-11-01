#coding=utf-8
# -*- coding: utf-8 -*-
import os
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
        bShowJieba = True
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

        #另用顏色與KeyWord的Mapping 將其著色

        for key in self.dicColorMapKeyWordList.keys():
            cr = key
            lst = self.dicColorMapKeyWordList[cr]
            fmt = QTextCharFormat()
            fmt.setBackground(cr)
            for keyword in lst:
                doc = self.document()
                curCursor = QTextCursor(doc)
                while True:
                    cursor = doc.find(keyword, curCursor)
                    if cursor.isNull():
                        break
                    cursor.setCharFormat(fmt)
                    curCursor = cursor

        if bShowJieba :
            self.moveCursor(QTextCursor.End)
            curCursor = self.textCursor()

            fm = self.currentCharFormat()
            # 增加分隔線
            curCursor.insertText(os.linesep, fm)
            curCursor.insertText(u"========================================", fm)
            curCursor.insertText(os.linesep, fm)

            #增加比較Jieba 的結果
            lstString = getJiebaCutList(qstr, True)

            lstcolorSwitch = [Qt.yellow, Qt.white]
            nColorSwitchIndex = 0
            for item in lstString:
                self.moveCursor(QTextCursor.End)
                curCursor = self.textCursor()
                nColorSwitchIndex=(nColorSwitchIndex+1) % len(lstcolorSwitch)
                fmt = QTextCharFormat()
                fmt.setBackground(lstcolorSwitch[nColorSwitchIndex])
                curCursor.insertText(item, fmt)
            self.setCurrentCharFormat(fm)