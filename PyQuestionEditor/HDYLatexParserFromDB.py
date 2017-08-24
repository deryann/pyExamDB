#coding=utf-8

import os
import codecs
from HDYQuestionParser import HDYQuestionParser, getListOfTagFromString
from HDYQuestionParserFromDB import HDYQuestionParserFromDB
from HDYLatexParser import HDYLatexParser
import sqlite3

constQuestionsTableName = u"EXAM01"
constQuestionTagRealtionTableName = u"question_tag_relationship"
constTagTableName = u"questiontags"

class HDYLatexParserFromDB(HDYLatexParser):
    def __init__(self,strInputFileName= u'test.sqlitedb', **args):
        HDYLatexParser.__init__(self, strInputFileName)
        self.conn = sqlite3.connect(strInputFileName)
        self.nCountQ = 0
        self.mainKey = None

        self.strMainSQL = u"select EXAMINFO_STR, question_id from " + constQuestionsTableName
        self.parserArgAsNewMainSQL(args)

    def parserArgAsNewMainSQL(self,args):
        if args.has_key(u'list_tag_str'):
            lstTagID = self.translateToTagIDs(args[u'list_tag_str'])
            strTagListSQL=(str(lstTagID).replace("[","(")).replace("]",")")
            strSQL = u"""SELECT a.EXAMINFO_STR, a.question_id FROM %s as b LEFT JOIN %s as a ON b.question_id=a.question_id
where b.tag_id IN %s
            """ % (constQuestionTagRealtionTableName, constQuestionsTableName,strTagListSQL)
            self.strMainSQL = strSQL


    def read(self):
        print("[HDYLatexParserFromDB][read]")
        self.mainKey = self.getRowsBySQL(self.strMainSQL)
        self.nCountQ = len(self.mainKey)
        print (self.mainKey)
        return u"This is Db Mode"

    def getmainkey(self,nIndex):
        row = self.mainKey[nIndex]
        return row[0]

    def getmainkeyid(self, nIndex):
        row = self.mainKey[nIndex]
        return row[1]

    def getReport(self):
        print("[HDYLatexParserFromDB][getReport]")
        print("[HDYLatexParserFromDB][getReport] Q count = %d" %(self.nCountQ,))


    def getQuestionTagList(self, nQIndex):
        print("[HDYLatexParserFromDB][getQuestionTagList]")
        self.currQuestion = self.getQuestionObject(nQIndex)
        return self.currQuestion.getListOfTag()

    def getCountOfQ(self):
        return self.nCountQ

    def getQuestionString(self, nIndex):
        strKey = self.getmainkey(nIndex)
        strSQL = u"select * from %s where EXAMINFO_STR = '%s' " %(constQuestionsTableName, strKey)
        row = self.getRowBySQL(strSQL)#TODO: Tranlate the row data into string

    def getQuestionObject(self, nIndex):
        qID = self.getmainkeyid(nIndex)
        qpt = HDYQuestionParserFromDB(qID,self.conn)
        return qpt

    def saveFileWithNewTag(self, dicNewTags):
        print("[HDYLatexParserFromDB][saveFileWithNewTag]")
        self.backupCurrentFile()
        for index in dicNewTags.keys():
            nQID = self.getmainkeyid(index)
            lst = dicNewTags[index]
            self.updateTagsToDB(index, lst)

    def updateTagsToDB(self, index, lstInput):
        """
        index 將 lstInput 內的Tag 更新到資料庫裡去
        :param index: 要更動的第幾題
        :param lstInput: 要的Tags全貌
        :return:
        """

        qpt = self.getQuestionObject(index)
        nQID = self.getmainkeyid(index)
        lstOriTag = qpt.getListOfTag()
        # 先整理出有多少要刪除，有多少要新增
        lstShouldDeleteRelationTag = list(set(lstOriTag) - set(lstInput))
        lstShouldAddRelationTag = list( set(lstInput) - set(lstOriTag) )
        # 將其Tags IDs 全部找出
        lstDeleteTagIDs = self.translateToTagIDs(lstShouldDeleteRelationTag)
        lstAddTagIDs = self.translateToTagIDs(lstShouldAddRelationTag)
        # 進行刪除SQL指令執行
        for idDelete in lstDeleteTagIDs:
            strDeleteSQL = u"DELETE FROM %s WHERE question_id=%d AND tag_id=%d" % (constQuestionTagRealtionTableName, nQID, idDelete)
            self.executeSQL(strDeleteSQL)
        # 進行新增指令執行
        for idInsert in lstAddTagIDs:
            strInsertSQL = u"""INSERT INTO %s (question_id, tag_id)
                                                VALUES ( %d, %d );
                                                """ % (constQuestionTagRealtionTableName, nQID, idInsert)
            self.executeSQL(strInsertSQL)
        self.commitDB()

    def executeSQL(self,strSQL):
        print (strSQL)
        self.conn.execute(strSQL)

    def commitDB(self):
        self.conn.commit()

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
        self.executeSQL(strInsertSQL)
        self.commitDB()
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

    def getQuestionIDInDB(self,strEXAMINFO_STR):
        nQID = -1
        strSQL ="select question_id, EXAMINFO_STR from %s where EXAMINFO_STR='%s' " % (constQuestionsTableName, strEXAMINFO_STR)
        row =self.getRowBySQL(strSQL)
        if row is not None:
            return row[0]
        else:
            return -1

    def appendTexFile(self,strFileName):
        fPt = HDYLatexParser(strFileName)
        fPt.read()
        fPt.getReport()
        for nIndex in range(fPt.getCountOfQ()):
            Qpt = HDYQuestionParser(fPt.getQuestionString(nIndex))
            print(Qpt.getEXAMINFO_STR())
            strSQL = "INSERT INTO EXAM01 %s" % Qpt.getSQLString()
            self.executeSQL(strSQL)
            self.conn.commit()
            #  Get question id
            nQId = self.getQuestionIDInDB(Qpt.getEXAMINFO_STR())
            if nQId != -1 :
                lstTags = Qpt.getListOfTag()
                lstTagsIds = self.translateToTagIDs(lstTags)             # find out tag id or add tag into table and get ID

                #Try to add relation between question and tag
                for nIdTag in lstTagsIds:
                    strInsertSQL = u"""
                                    INSERT INTO %s (question_id, tag_id)
                                    VALUES ( %d, %d );
                                    """ %(constQuestionTagRealtionTableName, nQId, nIdTag)
                    self.executeSQL(strInsertSQL)
                self.conn.commit()
                strInsertSQL = u"INSERT INTO %s (question_id,tag_id) VALUES (%d,%d)"
            else:
                print("[DB ERROR] we cannot find the row which just insert")
        print "Records created successfully";
