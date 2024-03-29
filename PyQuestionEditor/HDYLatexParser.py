﻿#coding=utf-8

import os
import codecs
from HDYQuestionParser import HDYQuestionParser


def isTexFileMode(strFileName):
    """
    利用輸入的副檔名，查詢是否為Tex file Mode
    :return:
    """
    if strFileName is None:
        return False
    if strFileName.find(u".tex") == -1:
        return False
    return True


def isSQLiteDBMode(strFileName):
    if strFileName is None:
        return False
    if strFileName.find(u".sqlitedb") == -1:
        return False
    return True

def isMySQLDBMode(strInput):
    if len(strInput) < 5 :
        return False
    if strInput[:5] == u'mysql':
        return True
    return False

##
#
# 針對檔案讀出做管理
# 支援兩種檔案 texfile, sqlite db file.
#

class HDYLatexParser:
    def __init__(self, strInputFileName):
        self.strFileName = strInputFileName

        self.nCountQ = 0
        self.lstCommentLineNum = [] # 記錄哪幾行為註解
        self.lstQStartLineNum = [] # 記錄哪幾行為問題開始處
        self.lstQEndLineNum = [] #記錄哪幾行為問題結束處

        self.ptFileStart = 0
        self.strAllLines = []

        if isTexFileMode(self.strFileName ):
            self.openFile()

        pass

    def newTemplate(self, strYear, strExam,  lstQstyle, strOutName):
        """
        輸入題型的編號起始值與終了值
        可以生成出一個空白的資料，並存入檔案之中
        """
        fPtOutput = codecs.open(strOutName, "w", "utf-8" )
        fPtOutput.write(self.getHeader())
        for i in range(len(lstQstyle)):
            fPtOutput.write(self.getQuestionsHeader())
            lst = lstQstyle [i]
            if lst[1].isdigit():
                #數字題號系列
                nStartNum = int(lst[1])
                nEndNum = int(lst[2])
                for num in range(nStartNum, nEndNum+1):
                    qPt = HDYQuestionParser("")
                    lstInput = []
                    lstInput.append(strYear)
                    lstInput.append(strExam)
                    lstInput.append(lst[0])
                    lstInput.append(str(num))

                    qPt.setlstExamInfo(lstInput,"")
                    fPtOutput.write(qPt.getQuestionString())
                    fPtOutput.write(os.linesep)
                    pass
            else:
                #非數字題號
                nStartNum = ord(lst[1])
                nEndNum = ord(lst[2])
                for num in range(nStartNum, nEndNum+1):
                    qPt = HDYQuestionParser("")
                    lstInput = []
                    lstInput.append(strYear)
                    lstInput.append(strExam)
                    lstInput.append(lst[0])
                    lstInput.append(chr(num))
                    qPt.setlstExamInfo(lstInput,"")
                    fPtOutput.write(qPt.getQuestionString())
                    fPtOutput.write(os.linesep)
            fPtOutput.write(self.getQuestionsTail())
        fPtOutput.close()

    def newTemplateByCsvInput(self, csvInput, strOutName=None):
        """
        輸入csv資料，根據每筆資料做輸出
        """
        if strOutName == None: #To  use nYears as Name
            qs=csvInput
            yearType = qs[u"年份"]
            yearTypeCounts = yearType.value_counts()
            print (yearTypeCounts.index)
            for item in yearTypeCounts.index:
                nYear = item
                strTempName = "q%03d.tex" % nYear
                yExam=qs[qs[u'年份']==nYear]
                self.newTemplateByCsvInputIntoOutName(yExam, strTempName)
            strOutName
        else:
            self.newTemplateByCsvInputIntoOutName(csvInput, strOutName)

    def transformAnsAsNum(self,strInput):
        dicReplaceAns= {u"(A)":u"(1)",
                        u"(B)":u"(2)",
                        u"(C)":u"(3)",
                        u"(D)":u"(4)",
                        u"(E)":u"(5)"}
        for item in dicReplaceAns.keys():
            strInput = strInput.replace(item, dicReplaceAns[item])
        return strInput

    def newTemplateByCsvInputIntoOutName(self, csvInput, strOutName):
        lstStrQuestionStyle = [u"單選",u"多選",u"填充"]
        lstChooseStyle = [u"單選",u"多選"]
        yExam =csvInput
        fPtOutput = codecs.open(strOutName, "w", "utf-8" )
        fPtOutput.write(self.getHeader())
        dicMapChap = {u'三角函數':u'B3C1三角', u'二次曲線':u'B4C4二次曲線', u'多項式':u'B1C2多項式函數', u'平面向量':u'B3C3平面向量', u'指數與對數':u'B1C3指對數函數', u'排列組合與':u'B2C2排列組合',
           u'數列與遞迴':u'B2C1數列級數',
           u'數學綜合概':u'綜合', u'機率':u'B2C3機率', u'直線與圓':u'B3C2直線與圓', u'矩陣與方程':u'B4C3矩陣', u'空間向量':u'B4C1空間向量', u'統計':u'B2C4數據分析', u'隨機變數':u'B5C1機率與統計'}

        for strqStyle in lstStrQuestionStyle:
            fPtOutput.write(self.getQuestionsHeader())
            qs = yExam[yExam[u'題型']==strqStyle]

            for index in range(len(qs.index)):
                row = qs.iloc[index]
                strExam =u'學測'
                qPt = HDYQuestionParser("")
                print (index)
                strQANS = row[u"答案"]
                if strqStyle in lstChooseStyle:
                    strQANS = self.transformAnsAsNum(strQANS)
                qPt.setQAns(strQANS)
                strTag99 = dicMapChap[row[u"章節（短）"]]
                qPt.setNewTagList([strTag99])

                lstInput = []
                nYear=row[u'年份']
                strYear = "%03d" % nYear
                lstInput.append(strYear)
                lstInput.append(strExam)
                lstInput.append(strqStyle)
                lstInput.append(row[u'題號'])

                lstAnsRateInfoInput = []
                for item in row['P':'LE']:
                    lstAnsRateInfoInput.append(item)

                qPt.setlstExamInfo(lstInput,"")
                lstRateInfo = lstAnsRateInfoInput[0:4]
                qPt.setlstAnsRateInfo(lstRateInfo,"")
                fPtOutput.write(qPt.getQuestionString())
                fPtOutput.write(os.linesep)

            fPtOutput.write(self.getQuestionsTail())
            fPtOutput.write(os.linesep)
        fPtOutput.close()

    def openFile(self):

        while True:
            try:
                self.fPt = codecs.open( self.strFileName, "r", "utf-8" )
                self.ptFileStart =self.fPt.tell()
                print("HDYLatexParser open file OK!!")
                break
            except IOError:
                print ("IOError")
                break

    def cleanReportData(self):
        self.lstCommentLineNum = [] # 記錄哪幾行為註解
        self.lstQStartLineNum = [] # 記錄哪幾行為問題開始處
        self.lstQEndLineNum = [] #記錄哪幾行為問題結束處

    def runReport(self):
        print("[runReport]")
        self.cleanReportData()
        self.fPt.seek(self.ptFileStart, os.SEEK_SET)
        self.strAllLines = self.fPt.readlines()
        for index in range(len(self.strAllLines)):
            if self.isComment(self.strAllLines[index]):
                self.lstCommentLineNum.append(index)
            elif self.isQStartLine(self.strAllLines[index]):
                self.lstQStartLineNum.append(index)
            elif self.isQEndLine(self.strAllLines[index]):
                self.lstQEndLineNum.append(index)
        self.nCountQ = len(self.lstQStartLineNum)
        pass

    def getCountOfQ(self):
        return self.nCountQ

    def isQStartLine(self, strTest):
        if u"\\begin{QUESTION}" in strTest:
            return True
        return False

    def isQEndLine(self, strTest):
        if u"\end{QUESTION}" in strTest:
            return True
        return False

    def isComment(self, strTest):
        if strTest==None:
            return False
        elif len(strTest)==0:
            return False
        elif strTest[0]=='%':
            return True
        else:
            return False
        return False

    def getReport(self):
        strReport = u""
        self.runReport()
        strReport+= (u"self.lstCommentLineNum " + str(self.lstCommentLineNum) + u"\n")
        strReport+=( u"self.lstQStartLineNum Count :" +str(len(self.lstQStartLineNum))+ str(self.lstQStartLineNum) + u"\n")
        strReport+=( u"self.lstQEndLineNum Count :" + str(len(self.lstQEndLineNum))+str(self.lstQEndLineNum) + u"\n")

        return strReport

    def getQuestionString(self, nIndex):
        if nIndex < len(self.lstQStartLineNum):
            lstQuestionStrings = self.strAllLines[self.lstQStartLineNum[nIndex]:self.lstQEndLineNum[nIndex]+1]
            strBuffer = u""
            for item in lstQuestionStrings:
                strBuffer+= item
            return strBuffer
        return None

    def getQuestionObject(self, nIndex):
        return  HDYQuestionParser(self.getQuestionString(nIndex))

    def getQuestionTagList(self, nIndex):
        self.currQustion = self.getQuestionObject(nIndex)
        return self.currQustion.getListOfTag()

    def read(self):
        self.fPt.seek(self.ptFileStart)
        return self.fPt.read()

    def getAllLines(self):
        strAllLines = self.fPt.readlines()
        return strAllLines

    def copyLatexFile(self):
        pass

        ##
        #
        # 找出原始的資料，一一行讀出，直到第一題begin
        # 確認該題有無新增Tags ，若是有，就將其寫到後面去


    def setTagToAllQuestion(self, strTag):
        pass

    def saveNewFileWithSelectedTag(self, strOutputFileName, lstSelectedTags):
        print("[saveNewFileWithSelectedTag]")
        fPtOutput = codecs.open(strOutputFileName, "w+", "utf-8" )
        for tagItem in lstSelectedTags:
            fPtOutput.write(u"\\begin{QUESTIONS} " +os.linesep)
            for i in range(self.getCountOfQ()):
                qPt = self.getQuestionObject(i)

                if qPt.isWithTag(tagItem):
                    for item in self.strAllLines[self.lstQStartLineNum[i]:self.lstQEndLineNum[i]+1]:
                        fPtOutput.write(item)
            fPtOutput.write(u"\\end{QUESTIONS}"+os.linesep)
        fPtOutput.close()
        pass
    ##
    # 存入新 Tag 資料到新檔案
    #
    def saveFileWithNewTag(self, dicNewTags):
        print("[saveFileWithNewTag]")
        self.backupCurrentFile()
        
        strFileName= self.strFileName
        fPtOutput = codecs.open(strFileName, "w", "utf-8" )

        #Prepare Title
        strStart= ""
        for item in self.strAllLines[0:self.lstQStartLineNum[0]]:
            strStart +=item

        fPtOutput.write(strStart)

        #Write all question one by one
        for i in range(self.getCountOfQ()):
            print ("Number i = %d " % (i))
            # Write from "i-1 th end line" to "i th start line"
            if i > 0:
                for item in self.strAllLines[self.lstQEndLineNum[i - 1] + 1: self.lstQStartLineNum[i]]:
                    fPtOutput.write(item)
            if not i in dicNewTags:
                #If question updated tag.
                print ("Start %d End %d" % (self.lstQStartLineNum[i], self.lstQEndLineNum[i]+1) )
                nEndNum = min(len(self.strAllLines), self.lstQEndLineNum[i]+1)
                for item in self.strAllLines[self.lstQStartLineNum[i]:nEndNum]:
                    fPtOutput.write(item)
            else:
                #If question WITHOUT updated tag.
                qPt = self.getQuestionObject(i)
                qPt.setNewTagList(dicNewTags[i])
                fPtOutput.write(qPt.getQuestionString())
                fPtOutput.write(os.linesep)
            pass
        #prepare end of file
        strEnd = ""
        for item in self.strAllLines[self.lstQEndLineNum[self.getCountOfQ()-1]+1:]:
            strEnd+=item

        fPtOutput.write(strEnd)
        fPtOutput.close()
        pass

    def setFromTagToAllQuestions(self, strQFrom, strfileName):
        print("[setFromTagToAllQuestions]")
        strFileName= strfileName
        fPtOutput = codecs.open(strFileName, "w+", "utf-8" )
        #Prepare Title
        strStart = self.getHeader()
        strStart += self.getQuestionsHeader()

        fPtOutput.write(strStart)

        for i in range(self.getCountOfQ()):
            qPt = self.getQuestionObject(i)
            qPt.setQFROM(strQFrom)
            fPtOutput.write(qPt.getQuestionString())
            if i!=self.getCountOfQ():
                fPtOutput.write(os.linesep)
            pass

        #prepare end of file
        strEnd = os.linesep
        strEnd += self.getQuestionsTail()
        fPtOutput.write(strEnd)

        fPtOutput.close()
        pass

    def backupCurrentFile(self):
        from time import gmtime, strftime
        strBachUpFileName = self.strFileName+strftime("%Y%m%d%H%M%S", gmtime())+".bak"
        import shutil
        shutil.copyfile(self.strFileName,strBachUpFileName)

    def getHeader(self):
        strHeader = "% !TEX encoding = UTF-8 Unicode" + os.linesep
        strHeader +="% !TEX TS-program = xelatex "
        strHeader += os.linesep
        return strHeader

    def getQuestionsHeader(self):
        return "\\begin{QUESTIONS}" + os.linesep

    def getQuestionsTail(self):
        return "\\end{QUESTIONS}"

    def setExamInfoForAllQuestions(self, strYear, strExam,strStyle,strStartNum):
        self.fPt.close()
        self.backupCurrentFile()
        strOutFileName= self.strFileName
        fPtOutput = codecs.open(strOutFileName, "w", "utf-8" )
        #Prepare Header
        strStart = self.getHeader()
        strStart += self.getQuestionsHeader()

        fPtOutput.write(strStart)

        for i in range(self.getCountOfQ()):
            qPt = self.getQuestionObject(i)
            lstInput = []
            lstInput.append(strYear)
            lstInput.append(strExam)
            lstInput.append(strStyle)
            if strStartNum.isdigit():
                nStartNum =int(strStartNum)
                lstInput.append(str(nStartNum+i))
            else:
                nStartNum = ord(strStartNum)
                lstInput.append(chr(nStartNum+i))
            qPt.setlstExamInfo(lstInput,"")
            fPtOutput.write(qPt.getQuestionString())
            if i!=self.getCountOfQ():
                fPtOutput.write(os.linesep)
            pass

        #prepare end of file
        strEnd = os.linesep
        strEnd += self.getQuestionsTail()
        fPtOutput.write(strEnd)

        fPtOutput.close()
        self.openFile()