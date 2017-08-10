#coding=utf-8

import os
import codecs
from HDYQuestionParser import HDYQuestionParser
from HDYLatexParser import HDYLatexParser
import sqlite3

constActionTableName = u"EXAM01"

class HDYLatexParserFromDB(HDYLatexParser):
    def __init__(self,strInputFileName= u'test.sqlitedb'):
        HDYLatexParser.__init__(self, strInputFileName)
        self.conn = sqlite3.connect(strInputFileName)
        self.nCountQ = 0
        self.mainKey = None


    def read(self):
        print("[HDYLatexParserFromDB][read]")
        cursor = self.conn.cursor()
        cursor.execute(u"select EXAMINFO_STR from " + constActionTableName)
        self.mainKey = cursor.fetchall()
        self.nCountQ = len(self.mainKey)
        print (self.mainKey)
        return u"This is Db Mode"

    def getmainkey(self,nIndex):
        row = self.mainKey[nIndex]
        return row[0]

    def getReport(self):
        print("[HDYLatexParserFromDB][getReport]")
        print("[HDYLatexParserFromDB][getReport] Q count = %d" %(self.nCountQ,))


    def getQuestionTagList(self, nQIndex):
        print("[HDYLatexParserFromDB][getQuestionTagList]")
        self.currQustion = HDYQuestionParser(self.getQuestion(nQIndex))
        return self.currQustion.getListOfTag()

    def getCountOfQ(self):
        return self.nCountQ

    def getQuestion(self,nIndex):
        cursor = self.conn.cursor()
        strKey = self.getmainkey(nIndex)
        strSQL = u"select FULLQUESTION from %s where EXAMINFO_STR = '%s' " %( constActionTableName, strKey)

        print (strSQL)
        cursor.execute(strSQL)
        rows = cursor.fetchall()
        if len (rows) == 1:
            row = rows[0]
            return row[0]
        else:
            print ("[HDYLatexParserFromDB][getQuestion(%d)] row count %d " %(nIndex,cursor.rowcount))
            return ""

    def saveFileWithNewTag(self, dicNewTags):
        return

    def setExamInfoForAllQuestions(self, strYear, strExam, strStyle, strStartNum):
        print("[HDYLatexParserFromDB][setExamInfoForAllQuestions][DO NOT SUPPORT THIS FUNCTION]")
        pass

    def setFromTagToAllQuestions(self, strQFrom, strfileName):
        print("[HDYLatexParserFromDB][setFromTagToAllQuestions][DO NOT SUPPORT THIS FUNCTION]")
        pass
