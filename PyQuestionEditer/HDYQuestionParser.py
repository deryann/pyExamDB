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
        self.strQFROM  = self.getStringFromEnvTag("QFROM")
        self.strQTAGS = self.getStringFromEnvTag("QTAGS")
        self.strQANS  = self.getStringFromEnvTag("QANS")
        self.strQSOL  = self.getStringFromEnvTag("QSOL")
        self.strQSOL2 = self.getStringFromEnvTag("QSOL2")
        self.lstNewTags =[]
        pass

    def setNewTagList(self, lstNewTagInput):
        self.lstNewTags = lstNewTagInput[:]

    def setQFROM(self, strInput):
        self.strQFROM = strInput

    def getEnvString(self, strEnvName, strEnvContent):
        strBuffer = "        \\begin{%s}%s            %s%s        \\end{%s}%s" % (strEnvName,os.linesep,strEnvContent, os.linesep, strEnvName, os.linesep)
        return strBuffer

    def getQuestionString(self):
        strBuffer  =u""
        strBuffer += self.getEnvString(u"QBODY", self.strQBODY)
        strBuffer += self.getEnvString(u"QFROM", self.strQFROM)
        strBuffer += self.getEnvString(u"QTAGS", self.strQTAGS)
        strBuffer += self.getEnvString(u"QANS", self.strQANS)
        strBuffer += self.getEnvString(u"QSOL", self.strQSOL)
        strBuffer += self.getEnvString(u"QSOL2", self.strQSOL2)
        strQ = u"    \\begin{QUESTION}%s%s%s    \\end{QUESTION}%s" %(os.linesep, strBuffer, os.linesep,os.linesep)
        print ("[getQuestionString] get question content")
        print (strBuffer)
        print ("[getQuestionString]")
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
        strReFindString = u"\\\\begin{" + strEnvTagName+ "}"+"(.*?)"
        strReFindString += u"\\\\end{" +strEnvTagName +"}"
        lst = re.findall(strReFindString, self.strBuffer, re.DOTALL)
        if len(lst) == 0:
            print("[getStringFromEnvTag] Env "+strEnvTagName+" fail!" )
            return ""
        else:
            strBuffer = lst[0].strip()
            return strBuffer
