#coding=utf-8

import os
import codecs
import re
import timeit
from HDYQuestionParser import HDYQuestionParser, getListOfTagFromString
from HDYQuestionParserFromDB import HDYQuestionParserFromDB
from HDYLatexParser import HDYLatexParser
from HDYLatexParserFromDB import HDYLatexParserFromDB
from TexToPNG.PNGMaker import PNGMaker
import sqlite3

constQuestionsTableName = u"EXAM01"
constQuestionTagRealtionTableName = u"question_tag_relationship"
constTagTableName = u"questiontags"

constdefaultname = u"test.sqlitedb"
constLogFile = u"HDYlogger.log"

strTikzTemplate = u"""\\begin{tikzpicture}%s
\\end{tikzpicture}

"""

def getListOfTikzFromString(strInput):
    # 找出所有行 \\begin{tikzpicture} 與 \\end{tikzpicture} 夾住的所有
    lst = re.findall(u"\\\\begin{tikzpicture}(.*?)\\\\end{tikzpicture}", strInput, re.DOTALL)
    return lst


def runSavePNG(qpt):
    """
    找出所有含有tikz圖形的，將其編輯利用latex 編輯成圖形
    :param qpt:
    :return:
    """
    strQBODY = qpt.getQBODY()
    lst = getListOfTikzFromString(strQBODY)
    nQID = qpt.question_id

    if len(lst)!=0:
        nIndex = 0
        for item in lst:
            strExamInfo = qpt.getEXAMINFO_SRING_FOR_PATH()
            strOutFileName = u"DBWebPics\QID_%d_pic_%d.png" % (nQID, nIndex)
            strTikz = strTikzTemplate %(item,)
            pngMaker = PNGMaker(strTikz, strOutFileName)
            pngMaker.runPNGMaker()
            nIndex+=1
    pass


def runSavePNG2(qpt):
    """
    For QSOL
    :param qpt:
    :return:
    """
    lstQSOL = qpt.getListOfQSOLs()
    lstQSOLID = qpt.getListOfQSOLsID()
    nQSOL = len(lstQSOL)
    for k in range(nQSOL):
        strQSOL =lstQSOL[k]
        nQSOLID =lstQSOLID[k]

        lst = getListOfTikzFromString(strQSOL)
        if len(lst)!=0:
            nIndex = 0
            for item in lst:
                strExamInfo = qpt.getEXAMINFO_SRING_FOR_PATH()
                nQID = qpt.question_id
                strOutFileName = u"DBWebPics\SOLID_%d_pic_%d.png" % (nQSOLID, nIndex)
                strTikz = strTikzTemplate %(item,)
                pngMaker = PNGMaker(strTikz, strOutFileName)
                pngMaker.runPNGMaker()
                nIndex+=1
                print (strOutFileName+u" OK!!"+os.linesep)
    pass


def runPNGForEachQBODY():
    dbLatex = HDYLatexParserFromDB(constdefaultname)
    dbLatex.read()
    nCountTikz = 0
    with codecs.open(constLogFile,"w", "utf-8") as fpt:
        nCount = dbLatex.nCountQ
        for i in range(nCount):
            qPt = dbLatex.getQuestionObject(i)
            runSavePNG(qPt)
            print ((u"No %d :"+os.linesep) %(i,))
            print (qPt.getEXAMINFO_STR())
            strQBODY =qPt.getQBODY()
            lst = getListOfTikzFromString(strQBODY)
            nCountTikz+=len(lst)
            print ("======================================")
            strlog = (u"NO %d QBODY have %d Tikz ENV !" + os.linesep) % (i, len(lst))
            fpt.write(strlog)
        strlog = (u"All QBODY have %d Tikz ENV !" + os.linesep) % (nCountTikz,)
        fpt.write(strlog)

    pass

def runPNGForEachQSOL():
    """
    ONLY for QSOL
    :return:
    """
    dbLatex = HDYLatexParserFromDB(constdefaultname)
    dbLatex.read()
    nCount = dbLatex.nCountQ
    for i in range(nCount):
        qPt = dbLatex.getQuestionObject(i)
        runSavePNG2(qPt)
    pass

def exportAllYearContentFromDB():
    dbLatex = HDYLatexParserFromDB(constdefaultname)
    dbLatex.read()
    nCount = dbLatex.nCountQ
    for i in range(nCount):
        qPt = dbLatex.getQuestionObject(i)

def runAllPictures():
    #run all pictures
    print("Run For AllQuestion Runing....Please wait...")
    timer_start = timeit.default_timer()

    runPNGForEachQBODY()
    runPNGForEachQSOL()

    timer_end = timeit.default_timer()
    print("This program Time usage:", timer_end - timer_start, " sec(s)")

def checkAllQuestioForMathJax():
    timer_start = timeit.default_timer()
    dbLatex = HDYLatexParserFromDB(constdefaultname)
    dbLatex.read()
    nCount = dbLatex.nCountQ
    for i in range(nCount):
        qPt = dbLatex.getQuestionObject(i)
        checkWordForMathJax(qPt)

    timer_end = timeit.default_timer()
    print("This program Time usage:", timer_end - timer_start, " sec(s)")

def checkWordForMathJax(qPt):
    strQBODY = qPt.getQBODY()
    if strQBODY.find('>')!=-1 or strQBODY.find('<')!=-1:
        strReturn  = (u"QID:%d %s") % (qPt.question_id, qPt.getQBODY())
        with codecs.open(constLogFile, "a", "utf-8") as fpt:
            fpt.write(strReturn)
            fpt.write(os.linesep)

if __name__ == '__main__':
    #runAllPictures()
    checkAllQuestioForMathJax()