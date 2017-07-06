import os
import codecs
from HDYQuestionParser import HDYQuestionParser


##
#
# 針對檔案讀出做管理
#
#
class HDYLatexParser:
    def __init__(self, strFileName):
        self.strFileName = strFileName

        self.nCountQ = 0

        self.lstCommentLineNum = [] # 記錄哪幾行為註解
        self.lstQStartLineNum = [] # 記錄哪幾行為問題開始處
        self.lstQEndLineNum = [] #記錄哪幾行為問題結束處

        self.ptFileStart = 0
        self.strAllLines = []
        while True:
            try:
                self.fPt = codecs.open( strFileName, "r", "utf-8" )
                self.ptFileStart =self.fPt.tell()
                print("HDYLatexParser open file OK!!")
                break
            except IOError:
                print ("IOError")
                break
        print("__init__ OK!!")
        pass

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

    def getQuestion(self, nIndex):
        if nIndex < len(self.lstQStartLineNum):
            lstQuestionStrings = self.strAllLines[self.lstQStartLineNum[nIndex]:self.lstQEndLineNum[nIndex]+1]
            strBuffer = u""
            for item in lstQuestionStrings:
                strBuffer+= item
            return strBuffer
        return None

    def getQuestionTagList(self, nIndex):
        strBuffer = self.getQuestion(nIndex)
        self.currQustion = HDYQuestionParser(strBuffer)
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

                strBuffer = self.getQuestion(i)
                qPt = HDYQuestionParser(strBuffer)

                if qPt.isWithTag(tagItem):
                    for item in self.strAllLines[self.lstQStartLineNum[i]:self.lstQEndLineNum[i]+1]:
                        fPtOutput.write(item)
            fPtOutput.write(u"\\end{QUESTIONS}"+os.linesep)
        fPtOutput.close()
        pass
    ##
    # 存入新 Tag 資料到新檔案
    #
    def saveNewFileWithNewTag(self, dicNewTags):
        print("[saveNewFileWithNewTag]")
        strFileName= "TestNewTagsOutPut.tex"
        fPtOutput = codecs.open(strFileName, "w+", "utf-8" )

        #Prepare Title
        strStart= ""
        for item in self.strAllLines[0:self.lstQStartLineNum[0]]:
            strStart +=item

        fPtOutput.write(strStart)

        for i in range(self.getCountOfQ()):
            if not i in dicNewTags:
                for item in self.strAllLines[self.lstQStartLineNum[i]:self.lstQEndLineNum[i]+1]:
                    fPtOutput.write(item)
                pass
            else:
                strBuffer = self.getQuestion(i)
                qPt = HDYQuestionParser(strBuffer)
                qPt.setNewTagList(dicNewTags[i])
                fPtOutput.write(qPt.getQuestionStringv2())
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
        strStart = "% !TEX encoding = UTF-8 Unicode" + os.linesep
        strStart +="% !TEX TS-program = xelatex "
        strStart += os.linesep
        strStart += "\\begin{QUESTIONS}"
        strStart += os.linesep

        fPtOutput.write(strStart)

        for i in range(self.getCountOfQ()):
            strBuffer = self.getQuestion(i)
            qPt = HDYQuestionParser(strBuffer)
            qPt.setQFROM(strQFrom)
            fPtOutput.write(qPt.getQuestionString())
            if i!=self.getCountOfQ():
                fPtOutput.write(os.linesep)
            pass

        #prepare end of file
        strEnd = os.linesep
        strEnd += "\\end{QUESTIONS}"
        fPtOutput.write(strEnd)

        fPtOutput.close()
        pass

    def setExamInfoForAllQuestions(self, strYear, strExam,strStyle,nStartNum):
        strFileName= "AddExamInfoTemp.tex"
        fPtOutput = codecs.open(strFileName, "w+", "utf-8" )
        #Prepare Header
        strStart = "% !TEX encoding = UTF-8 Unicode" + os.linesep
        strStart +="% !TEX TS-program = xelatex "
        strStart += os.linesep
        strStart += "\\begin{QUESTIONS}"
        strStart += os.linesep

        fPtOutput.write(strStart)

        for i in range(self.getCountOfQ()):
            strBuffer = self.getQuestion(i)
            qPt = HDYQuestionParser(strBuffer)
            lstInput = []
            lstInput.append(strYear)
            lstInput.append(strExam)
            lstInput.append(strStyle)
            lstInput.append(str(nStartNum+i))
            qPt.setlstExamInfo(lstInput,"")
            fPtOutput.write(qPt.getQuestionString())
            if i!=self.getCountOfQ():
                fPtOutput.write(os.linesep)
            pass

        #prepare end of file
        strEnd = os.linesep
        strEnd += "\\end{QUESTIONS}"
        fPtOutput.write(strEnd)

        fPtOutput.close()

