#coding=utf-8

import os
import codecs
import re
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
constLogFile = u"tikzcounting.log"

strTikzTemplate = u"""\\begin{tikzpicture}%s
\\end{tikzpicture}

"""

def getListOfTikzFromString(strInput):
    # 找出所有行 \\begin{tikzpicture} 與 \\end{tikzpicture} 夾住的所有
    lst = re.findall(u"\\\\begin{tikzpicture}(.*?)\\\\end{tikzpicture}", strInput, re.DOTALL)
    return lst


def runSavePNG(qpt):
    strQBODY = qpt.getQBODY()
    lst = getListOfTikzFromString(strQBODY)
    if len(lst)!=0:
        nIndex = 0
        for item in lst:
            strExamInfo = qpt.getEXAMINFO_SRING_FOR_PATH()
            nQID = qpt.question_id
            strOutFileName = u"DBWebPics\QID_%d_pic_%d.png" % (nQID, nIndex)
            strTikz = strTikzTemplate %(item,)
            pngMaker = PNGMaker(strTikz, strOutFileName)
            pngMaker.runPNGMaker()

            nIndex+=1
    pass


def main():
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

if __name__ == '__main__':
    main()