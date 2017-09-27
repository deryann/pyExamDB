#coding=utf-8

import os
import codecs
from HDYQuestionParser import HDYQuestionParser, getListOfTagFromString
from HDYQuestionParserFromDB import HDYQuestionParserFromDB
from HDYLatexParser import HDYLatexParser
import sqlite3
from datetime import datetime
import re

constQuestionsTableName = u"EXAM01"
constQuestionTagRealtionTableName = u"question_tag_relationship"
constTagTableName = u"questiontags"
constlstStyle = [u'單選', u'多選', u'填充']
constLatexHeader =u"""% !TEX encoding = UTF-8 Unicode
% !TEX TS-program = xelatex
"""
constLatexTailer =u""
constLatexStyleHeader = u"\\begin{QUESTIONS}"+os.linesep
constLatexStyleTailer= u"\\end{QUESTIONS}"+os.linesep

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
        print(u"qID = %d" %(qID,))
        qpt = self.getQuestionObjectByQID(qID)
        return qpt

    def getQuestionObjectByQID(self, qID):
        return HDYQuestionParserFromDB(qID, self.conn)

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

    def saveSqliteDBIntoTexFileByYears(self, nStart, nEnd):
        conn = sqlite3.connect(self.strFileName)

        lstFileNameList = []
        for number in range(nStart, nEnd+1):
            strFileName = u"Exam01All\\q%03d.tex" % number

            if os.path.isfile(strFileName):
                #backup it
                from time import gmtime, strftime
                strBachUpFileName = strFileName + u"."+ strftime("%Y%m%d%H%M%S", gmtime()) + u".bak"
                import shutil
                shutil.copyfile(strFileName, strBachUpFileName)

            with codecs.open(strFileName, "w", "utf-8") as fpt:
                fpt.write(constLatexHeader)
                for strStyle in [u'單選', u'多選', u'填充']:
                    fpt.write(constLatexStyleHeader)
                    strSQL = u"""select EXAMINFO_STR, question_id from %s 
                                 where  EXAMINFO_YEAR=%d and EXAMINFO_QUESTION_STYLE = '%s'
                                 ORDER BY LENGTH(EXAMINFO_QUESTION_NUMBER), EXAMINFO_QUESTION_NUMBER
                                """ % (constQuestionsTableName, number, strStyle )
                    rows = self.getRowsBySQL(strSQL)
                    count  = len(rows)
                    for i in range(count):
                        row = rows[i]
                        qID = row[1]
                        qpt = HDYQuestionParserFromDB(qID, self.conn)
                        qpt.prepareData()
                        fpt.write(qpt.getQuestionString())
                        fpt.write(os.linesep)
                    fpt.write(constLatexStyleTailer)
                fpt.write(constLatexTailer)
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

    def getDictTagIDMapQuestionCount(self):
        strSQL = u"""SELECT question_tag_relationship.tag_id, count(question_tag_relationship.tag_id) as tag_total FROM question_tag_relationship 
                    LEFT JOIN questiontags ON question_tag_relationship.tag_id = questiontags.tag_id 
                    GROUP BY question_tag_relationship.tag_id"""
        return self.getDictForTwoCol(strSQL)

    def getDictForTwoCol(self, strSQL):
        """
        將兩個col 的取出一個變為Key 一個變為 value 的結構
        :param strSQL:
        :return:
        """
        dicR = {}

        rows = self.getRowsBySQL(strSQL)
        for row in rows:
            dicR[row[0]] = row[1]
        return dicR

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

    def existedSol(self, nQID, strSol):
        strSQL = u"""SELECT sol_id from questionsols where question_id=%d and SOL_STR ='%s'
        """ % (nQID, self.correctSQL(strSol))
        row=self.getRowBySQL(strSQL)
        return row != None

    def getSolSTR(self, nSolID):
        strSQL = u"""SELECT SOL_STR from questionsols where sol_id=%d 
        """ % (nSolID, )
        row=self.getRowBySQL(strSQL)
        return row[0]

    def getSOLID(self, strSol):
        lst = re.findall(u"\\[SOLID\\=(.*?)\\]", strSol, re.DOTALL)
        if len(lst)!=1:
            return -1
        else:
            return int(lst[0])

    def cleanSolString(self, strSol):
        if len(strSol)==0: return strSol
        if strSol[0] != u'[':
            return strSol

        for k in range(1,len(strSol) ):
            if strSol[k] == ']':
                return strSol[k+1:]

        return strSol

    def shouldUpdateSol(self, nSOLID, solitem):
        strSolInDB = self.getSolSTR(nSOLID)
        strCompareString = self.cleanSolString(solitem)
        return strSolInDB.strip() != strCompareString.strip()

    def importTexFile(self, strFileName, bSimulate = False):
        #先整理一個大表
        print(u"[importTexFile][%s]" %(strFileName,))
        dicUpdateQuestionidMapUpdateDic={}
        fPt = HDYLatexParser(strFileName)
        fPt.read()
        fPt.getReport()
        nCount =0
        lst = []
        dicNeedToUpdateQBODY = {}
        dicNeedToUpdateQANS = {}
        for nIndex in range(fPt.getCountOfQ()):
            qptInFile = HDYQuestionParser(fPt.getQuestionString(nIndex))
            print(qptInFile.getEXAMINFO_STR())
            nQId = self.getQuestionIDInDB(qptInFile.getEXAMINFO_STR())
            if nQId != -1:
                #Check QBODY ANS 需不需要更正
                qptInDB = self.getQuestionObjectByQID(nQId)
                if qptInFile.getQBODY()!=qptInDB.getQBODY():
                    dicNeedToUpdateQBODY[nQId]=qptInFile.getQBODY()
                if qptInFile.getQANS()!=qptInDB.getQANS():
                    dicNeedToUpdateQANS[nQId] = qptInFile.getQANS()

                #找出詳解的部分
                lst = qptInFile.getListOfQSOLs()
                if len(lst)!=0:
                    print ("QID %d : have %d Sols"%( nQId, len(lst)))
                    dicUpdateQuestionidMapUpdateDic[nQId] = lst
                    nCount += len(lst)

            #check 該解法是不是已經在 Database 裡面 需要Insert 還是Update
            lstNeedToInsertSol=[]
            dicNeedToUpdateSol={}

            for solitem in lst:
                nSOLID = self.getSOLID(solitem)

                if nSOLID==-1:
                    if not self.existedSol(nQId, solitem):
                        lstNeedToInsertSol.append(solitem)
                else:
                    if self.shouldUpdateSol(nSOLID, solitem):
                        dicNeedToUpdateSol[nSOLID] = self.cleanSolString(solitem)
                    else:
                        pass
            if bSimulate:
                print(u"=======Simulate======")
                print(u"lstNeedToInsertSol = " + unicode(lstNeedToInsertSol))
                print(u"dicNeedToUpdateSol = " + unicode(dicNeedToUpdateSol))
                print(u"=====================")
            else:
                #Insert 該 Insert
                for solitem in lstNeedToInsertSol:
                    strInsertSQL = u"""
                                    INSERT INTO %s (question_id, SOL_STR,SOL_AUTHOR,SOL_USEFUL,SOL_DATETIME)
                                    VALUES ( %d, '%s', '%s',%d, '%s');
                                    """ % (u"questionsols", nQId, self.correctSQL(solitem), u'HDY',0, datetime.now())
                    self.executeSQL(strInsertSQL)
                #Update 那些有SOLID 的
                for solid in dicNeedToUpdateSol.keys():
                    strUpdateSQL = u"""UPDATE %s SET SOL_STR='%s', SOL_DATETIME='%s' WHERE sol_id = %d 
                    """ % (u"questionsols", self.correctSQL(dicNeedToUpdateSol[solid]), datetime.now(), solid)
                    self.executeSQL(strUpdateSQL)

                if len(lstNeedToInsertSol)!= 0 or len(dicNeedToUpdateSol.keys())!= 0:
                    self.commitDB()
        #Update QBODY
        if bSimulate:
                print(u"=======Simulate======")
                print(u"dicNeedToUpdateQBODY = "+ unicode(dicNeedToUpdateQBODY))
                print(u"=====================")
        else:
            for qid in dicNeedToUpdateQBODY.keys():
                strUpdateSQL = u"""UPDATE %s SET QBODY='%s' WHERE question_id = %d 
                """ % (constQuestionsTableName, self.correctSQL(dicNeedToUpdateQBODY[qid]), qid)
                self.executeSQL(strUpdateSQL)

            for qid in dicNeedToUpdateQANS.keys():
                strUpdateSQL = u"""UPDATE %s SET QANS='%s' WHERE question_id = %d 
                """ % (constQuestionsTableName, self.correctSQL(dicNeedToUpdateQANS[qid]), qid)
                self.executeSQL(strUpdateSQL)

            self.commitDB()
        return len(dicUpdateQuestionidMapUpdateDic.keys()), nCount

    def appendTexFile(self,strFileName):
        """
        將檔案裡資料無條件加入 DB
        :param strFileName:
        :return:
        """
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

    def correctSQL(self,strInput):
        strOutput = strInput.replace("'", "''")
        return strOutput

    def tagWeightGiver(self):
        """
        取出冊作千位數 章當百位數 節當十位數 作為Weight
        :return:
        """
        strSQL = u" SELECT TAG_STR from questiontags where TAG_STR LIKE 'B%C%'"
        rows = self.getRowsBySQL(strSQL)
        count = len(rows)
        for i in range(count):
            row = rows[i]
            strTag = row[0]
            lst = re.findall(u"\d+", strTag)
            nTotalW = 0
            if len(lst)==3:
                nTotalW = int (lst[0]) * 1000+ int(lst[1]) *100 + int(lst[2])*10
            elif len(lst) == 2:
                nTotalW = int(lst[0]) * 1000 + int(lst[1]) * 100

            strUpdateSQL = u"""UPDATE questiontags SET TAG_SORTED_W = %d  
                                WHERE TAG_STR='%s'""" % (nTotalW, strTag)
            self.executeSQL(strUpdateSQL)
        self.commitDB()
