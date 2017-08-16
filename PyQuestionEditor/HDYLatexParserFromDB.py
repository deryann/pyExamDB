#coding=utf-8

import os
import codecs
from HDYQuestionParser import HDYQuestionParser, getListOfTagFromString
from HDYLatexParser import HDYLatexParser
import sqlite3

constQuestionsTableName = u"EXAM01"
constQuestionTagRealtionTableName = u"question_tag_relationship"
constTagTableName = u"questiontags"

class HDYLatexParserFromDB(HDYLatexParser):
    def __init__(self,strInputFileName= u'test.sqlitedb'):
        HDYLatexParser.__init__(self, strInputFileName)
        self.conn = sqlite3.connect(strInputFileName)
        self.nCountQ = 0
        self.mainKey = None


    def read(self):
        print("[HDYLatexParserFromDB][read]")
        strSQL = (u"select EXAMINFO_STR from " + constQuestionsTableName)
        self.mainKey = self.getRowsBySQL(strSQL)
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
        strKey = self.getmainkey(nIndex)
        strSQL = u"select FULLQUESTION from %s where EXAMINFO_STR = '%s' " %(constQuestionsTableName, strKey)
        rows = self.getRowsBySQL(strSQL)
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
                strSQL = u"select FULLQUESTION from %s where  EXAMINFO_YEAR=%d ORDER BY EXAMINFO_QUESTION_STYLE, EXAMINFO_QUESTION_NUMBER" % (constQuestionsTableName, number)
                """
                TODO: 
                待解問題一:單選多選選填的排序情形
                待解問題二：TagList 似乎有次序亂掉的情形，要注意一下如何讓Tag的存入情形與次序唯一
                select FULLQUESTION from EXAM01 where  EXAMINFO_YEAR=106 ORDER BY EXAMINFO_QUESTION_STYLE, EXAMINFO_QUESTION_NUMBER
                """
                rows = self.getRowsBySQL(strSQL)
                count  = len(rows)
                for i in range(count):
                    row = rows[i]
                    fpt.write(row[0])
                    fpt.write(os.linesep)

        print "Records created successfully";
        pass

    def getRowsBySQL(self,strSQL):
        """
        Support SQL Select command to get rows.
        :param strSQL:
        :return:
        """
        cursor = self.conn.cursor()
        print (strSQL)
        cursor.execute(strSQL)
        rows = cursor.fetchall()
        print (u"There are %d rows in query!" % len(rows))
        return rows

    def getRowBySQL(self,strSQL):
        cursor = self.conn.cursor()
        print (strSQL)
        cursor.execute(strSQL)
        row = cursor.fetchone()
        return row

    def handleNoTagInDB(self, strTag):
        #insert tag
        strInsertSQL = u"""INSERT INTO %s (TAG_STR)
                                VALUES ( '%s' );""" % (constTagTableName, strTag)
        self.conn.execute(strInsertSQL)
        self.conn.commit()
        #reget id
        strSQL = "select tag_id from %s where TAG_STR = '%s'" % (constTagTableName, strTag)
        row = self.getRowBySQL(strSQL)
        if row is not None:
            return row[0]
        else:
            return -1

    def translateToTagIDs(self,lstTags):
        lstReturn = []
        for item in lstTags:
            strSQL = "select tag_id from %s where TAG_STR = '%s'" %(constTagTableName, item)
            row = self.getRowBySQL(strSQL)
            if row is None:
                nId = self.handleNoTagInDB(item)
                if nId !=-1:
                    lstReturn.append(nId)
            else:
                lstReturn.append(row[0])

        return lstReturn


    def refreshTagTableInDB(self):
        """
        試著將EXAM01的QUESTION主體中的QTAG 整理出來 QUESTIONTAG_RELATION TABLE QUESTIONTAG TABLE

        :return:
        """
        strSQL = "select question_id, EXAMINFO_STR, QTAGS from %s " % (constQuestionsTableName,)
        rows = self.getRowsBySQL(strSQL)
        count = len(rows)
        #for i in range(count):
        for i in range(count):
            row = rows[i]
            nQId = row[0]
            strTAGS = row[2]
            lstTags = getListOfTagFromString(strTAGS)
            lstTagsIds = self.translateToTagIDs(lstTags)
            for nIdTag in lstTagsIds:
                strInsertSQL = u"""
                                INSERT INTO %s (question_id, tag_id)
                                VALUES ( %d, %d );
                                """ %(constQuestionTagRealtionTableName, nQId, nIdTag)
                print (strInsertSQL)
                self.conn.execute(strInsertSQL)
            self.conn.commit()

        pass