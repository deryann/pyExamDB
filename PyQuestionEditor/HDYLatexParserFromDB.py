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
        self.currQuestion = HDYQuestionParser(self.getQuestion(nQIndex))
        return self.currQuestion.getListOfTag()

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

    def saveSqliteDBIntoTexFileByYears(self):
        conn = sqlite3.connect(self.strFileName)

        lstFileNameList = []
        # for number in range(91,107):
        #for number in range(91, 107):
        for number in range(106, 107):
            strFileName = u"Exam01All\\2q%03d.tex" % number

            if os.path.isfile(strFileName):
                #backup it
                from time import gmtime, strftime
                strBachUpFileName = strFileName + u"."+ strftime("%Y%m%d%H%M%S", gmtime()) + u".bak"
                import shutil
                shutil.copyfile(strFileName, strBachUpFileName)

            with codecs.open(strFileName, "w", "utf-8") as fpt:
                cursor = self.conn.cursor()
                strSQL = u"select FULLQUESTION from %s where  EXAMINFO_YEAR=%d ORDER BY EXAMINFO_QUESTION_STYLE, EXAMINFO_QUESTION_NUMBER" % (constActionTableName, number)
                """
                TODO: 
                待解問題一:單選多選選填的排序情形
                待解問題二：TagList 似乎有次序亂掉的情形，要注意一下如何讓Tag的存入情形與次序唯一
                select FULLQUESTION from EXAM01 where  EXAMINFO_YEAR=106 ORDER BY EXAMINFO_QUESTION_STYLE, EXAMINFO_QUESTION_NUMBER
                
                """
                print (strSQL)
                cursor.execute(strSQL)
                rows = cursor.fetchall()
                print (u"There are %d rows in query!" % len(rows))
                count  = len(rows)
                for i in range(count):
                    row = rows[i]
                    fpt.write(row[0])
                    fpt.write(os.linesep)

        print "Records created successfully";
        pass