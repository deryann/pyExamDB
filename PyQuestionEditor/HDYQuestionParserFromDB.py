# coding=utf-8
import os, codecs, re
from HDYQuestionParser import HDYQuestionParser, generateTagTexStringFromList

constQuestionsTableName = u"EXAM01"
constQuestionTagRealtionTableName = u"question_tag_relationship"
constTagTableName = u"questiontags"

bShowSQLLogPrint = False


class HDYQuestionParserFromDB(HDYQuestionParser):
    def __init__(self, question_id, conn):
        self.conn = conn
        self.question_id = question_id  # question_id in DB
        self.lstSols = []
        self.lstSolsID = []
        HDYQuestionParser.__init__(self, None)

    def loadDicByQuestionIDFromDB(self):
        strSQL = u"select * from %s where question_id = %d " % (constQuestionsTableName, self.question_id)
        cursor = self.conn.cursor()
        self.logprint(strSQL)
        cursor.execute(strSQL)
        row = cursor.fetchone()
        import itertools
        field_names = [d[0].upper() for d in cursor.description]

        return dict(zip(field_names, row))

    def getListOfQSOLsID(self):
        return getListOfSOLFromString(self.strQSOLLIST)

    def getRowsBySQL(self, strSQL):
        """
        Support SQL Select command to get rows.
        :param strSQL:
        :return:
        """
        cursor = self.conn.cursor()
        self.logprint(strSQL)
        cursor.execute(strSQL)
        rows = cursor.fetchall()
        self.logprint(u"There are %d rows in query!" % len(rows))
        return rows

    def getRowBySQL(self, strSQL):
        cursor = self.conn.cursor()
        self.logprint(strSQL)
        cursor.execute(strSQL)
        row = cursor.fetchone()
        return row

    def loadQTAGS(self):
        """
        由資料庫裡面的所有資料獲得 lstOriginalTags, strQTAGS
        :return:
        """
        self.lstOriginalTags = []
        strSQL = u"""select b.TAG_STR from question_tag_relationship as a 
                        Left JOIN questiontags as b 
                        ON a.tag_id = b.tag_id 
                        where a.question_id = %d 
                        ORDER BY b.TAG_SORTED_W
                        """ % (self.question_id,)

        rows = self.getRowsBySQL(strSQL)
        for row in rows:
            self.lstOriginalTags.append(row[0])

        self.strQTAGS = generateTagTexStringFromList(self.lstOriginalTags)

    def getListOfTag(self):
        return self.lstOriginalTags

    def loadExamInfo(self):
        return [int(self.dicData['EXAMINFO_YEAR']), self.dicData['EXAMINFO_EXAM_TYPE'],
                self.dicData['EXAMINFO_QUESTION_STYLE'], self.dicData['EXAMINFO_QUESTION_NUMBER']]

    def loadExamAnsRateInfo(self):
        if (self.dicData['EXAMANSRATEINFO_P'] is None) or (self.dicData['EXAMANSRATEINFO_PH'] is None) or (
                self.dicData['EXAMANSRATEINFO_PM'] is None) or (self.dicData['EXAMANSRATEINFO_PL'] is None):
            return [None, None, None, None]
        return [int(self.dicData['EXAMANSRATEINFO_P']), int(self.dicData['EXAMANSRATEINFO_PH']),
                int(self.dicData['EXAMANSRATEINFO_PM']), int(self.dicData['EXAMANSRATEINFO_PL'])]

    def loadSols(self):
        strSQL = u"""select sol_id,SOL_STR FROM  questionsols  
                                where question_id = %d""" % (self.question_id,)
        rows = self.getRowsBySQL(strSQL)
        strBuffer = u''
        strTemplete = "\\begin{QSOL}[SOLID=%d]%s\\end{QSOL}" + os.linesep
        self.lstSols = []
        for row in rows:
            strBuffer += strTemplete % (row[0], row[1])
            self.lstSols.append(row[1])
            self.lstSolsID.append(row[0])

        self.strQSOLLIST = strBuffer

    def prepareData(self):
        self.dicData = self.loadDicByQuestionIDFromDB()
        self.nQID = self.dicData["QUESTION_ID"]
        self.strQBODY = self.dicData["QBODY"]
        self.strQFROMS = self.dicData["QFROMS"]

        self.strQANS = self.dicData["QANS"]
        self.loadSols()
        self.strQEMPTYSPACE = self.dicData["QEMPTYSPACE"]
        self.lstNewTags = []
        self.lstOriginalTags = []
        self.loadQTAGS()

        self.lstExamInfoParams = self.loadExamInfo()
        self.lstExamAnsRateInfoParams = self.loadExamAnsRateInfo()
        self.strExamInfoBODY = ""
        self.strExamAnsRateInfoBODY = ""
        pass

    def getListOfQSOLs(self):
        return self.lstSols

    def getListOfQSOLsID(self):
        return self.lstSolsID

    def logprint(self, trlog):
        if bShowSQLLogPrint:
            print(strlog)
