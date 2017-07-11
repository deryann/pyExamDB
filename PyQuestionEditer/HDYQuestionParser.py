import os, codecs, re


##
#
#  針對單一的Question String 做擷取
#
#

class HDYQuestionParser:
    def __init__(self, strInput):
        self.setQuestionString(strInput)
        pass

    def setQuestionString(self, strInput):
        self.strBuffer= strInput
        self.prepareData()

    def getQuestionString(self,):
        return self.strBuffer

    def prepareData(self):
        self.strQBODY = self.getStringFromEnvTag("QBODY")
        self.strQFROMS  = self.getStringFromEnvTag("QFROMS")
        self.strQTAGS = self.getStringFromEnvTag("QTAGS")
        self.strQANS  = self.getStringFromEnvTag("QANS")
        self.strQSOL  = self.getStringFromEnvTag("QSOL")
        self.strQSOL2 = self.getStringFromEnvTag("QSOL2")
        self.strQEMPTYSPACE= self.getStringFromEnvTag("QEMPTYSPACE")
        self.lstNewTags =[]
        self.lstExamInfoParams = self.getParamsListFromEnvTag("ExamInfo")
        self.lstExamAnsRateInfoParams = self.getParamsListFromEnvTag("ExamAnsRateInfo")
        self.strExamInfoBODY = ""
        self.strExamAnsRateInfoBODY = ""


        pass

    def setNewTagList(self, lstNewTagInput):
        self.lstNewTags = lstNewTagInput[:]

    def setQFROM(self, strInput):
        self.strQFROMS = strInput

    def getQBODY(self):
        return self.strQBODY

    def getQANS(self):
        return self.strQANS

    def getQSOL(self):
        return self.strQSOL

    def getEnvString(self, strEnvName, strEnvContent):
        if strEnvContent =='':
            strBuffer = "        \\begin{%s}%s        \\end{%s}%s" % (strEnvName, os.linesep, strEnvName, os.linesep)
        else:
            strBuffer = "        \\begin{%s}%s            %s%s        \\end{%s}%s" % (strEnvName,os.linesep,strEnvContent, os.linesep, strEnvName, os.linesep)
        return strBuffer

    def setlstExamInfo(self, lstParamsExamInfo, strBODY):
        self.lstExamInfoParams = lstParamsExamInfo
        self.strExamInfoBODY = strBODY
        pass

    def setlstAnsRateInfo(self, lstParams,strBODY):
        self.lstExamAnsRateInfoParams =lstParams
        self.strExamAnsRateInfoBODY = strBODY
        pass

    def getExamInfoString(self):
        strParams = u"{%s}{%s}{%s}{%s}" % (self.lstExamInfoParams[0],self.lstExamInfoParams[1],
                                           self.lstExamInfoParams[2],self.lstExamInfoParams[3])
        if self.strExamInfoBODY == "":
            strReturn = u"        \\begin{ExamInfo}%s%s        \\end{ExamInfo}%s" %( strParams, os.linesep,os.linesep)
        else:
            strReturn = u"        \\begin{ExamInfo}%s%s%s%s        \\end{ExamInfo}%s" %( strParams, os.linesep, self.strExamInfoBODY, os.linesep,os.linesep)
        return strReturn

    def getExamAnsRateInfoString(self):
        strParams =""

        for item in self.lstExamAnsRateInfoParams:
            strParam = "{%s}" % item
            strParams+=strParam

        if self.strExamInfoBODY == "":
            strReturn = u"        \\begin{ExamAnsRateInfo}%s%s        \\end{ExamAnsRateInfo}%s" %( strParams, os.linesep,os.linesep)
        else:
            strReturn = u"        \\begin{ExamAnsRateInfo}%s%s%s%s        \\end{ExamAnsRateInfo}%s" %( strParams, os.linesep, self.strExamInfoBODY, os.linesep,os.linesep)
        return strReturn

    def getQuestionString(self):
        strBuffer  =u""
        strBuffer += self.getExamInfoString()
        strBuffer += self.getExamAnsRateInfoString()
        strBuffer += self.getEnvString(u"QBODY", self.strQBODY)
        strBuffer += self.getEnvString(u"QFROMS", self.strQFROMS)
        strBuffer += self.getEnvString(u"QTAGS", self.strQTAGS)
        strBuffer += self.getEnvString(u"QANS", self.strQANS)
        strBuffer += self.getEnvString(u"QSOL", self.strQSOL)
        if self.strQSOL2 !="":
            strBuffer += self.getEnvString(u"QSOL2", self.strQSOL2)
        strBuffer += self.getEnvString(u"QEMPTYSPACE", self.strQEMPTYSPACE)
        strQ = u"    \\begin{QUESTION}%s%s    \\end{QUESTION}" %(os.linesep, strBuffer)
        print ("[getQuestionString start ] get question content")
        print (strBuffer)
        print ("[getQuestionString end]")
        return strQ

    def generateNewTagString(self):
        strBuffer = ""
        for item in self.lstNewTags:
            strTag = u"\\QTAG{%s} " % (item)
            strBuffer += strTag
        strTAGS = u"\\begin{QTAGS}%s\\end{QTAGS}" % strBuffer
        return strTAGS

    def getQuestionStringv2(self):
        strReturn = self.strBuffer
        #replace the newtags into new versoion
        if self.isThereQTAGEnv():
            newCTagsString = self.generateNewTagString()
            strEnvTagName = "QTAGS"
            strReFindString = u"\\\\begin{" + strEnvTagName+ "}"+"(.*?)"
            strReFindString += u"\\\\end{" +strEnvTagName +"}"
            lst = re.findall(strReFindString, self.strBuffer, re.DOTALL)
            srcString =u"\\begin{QTAGS}%s\\end{QTAGS}" % ( lst[0])
            strR = strReturn.replace(srcString, newCTagsString)
        else:
            strR = strReturn
            pass
        return strR
        pass

    def isThereQTAGEnv(self):
        return self.strBuffer.find( u"\\begin{QTAGS}") != -1

    def getListOfTag(self):
        strTags = self.strQTAGS
        #找出所有行 \\begin{QTAGS} 與 \\end{QTAGS} 夾住的所有
        lst = re.findall(u"QTAG{(.*?)}", strTags, re.DOTALL)
        return lst

    def isWithTag(self, inputTag):
        return inputTag in self.getListOfTag()

    def getStringFromEnvTag(self, strEnvTagName):
        if self.strBuffer == "":
            return ""
        strReFindString = u"\\\\begin{" + strEnvTagName+ "}"+"(.*?)"
        strReFindString += u"\\\\end{" +strEnvTagName +"}"
        lst = re.findall(strReFindString, self.strBuffer, re.DOTALL)
        if len(lst) == 0:
            print("[getStringFromEnvTag] Env "+strEnvTagName+" fail!" )
            return ""
        else:
            strReturn = lst[0].strip()
            return strReturn

    def getParamsListFromEnvTag(self, strEnvTagName):
        """
        Get the first line {%s}
        """
        lstReturn = []
        strEnvTagBody = self.getStringFromEnvTag(strEnvTagName)
        strReFindString = "{(.*?)}"
        strParams= strEnvTagBody.split('\n', 1)[0]
        lstReturn = re.findall(strReFindString, strParams, re.DOTALL)
        return lstReturn

