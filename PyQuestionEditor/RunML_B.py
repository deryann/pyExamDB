# -*- coding: utf-8 -*-
import os
import numpy as np
import codecs
import re
import operator
from LatexTextTool import *

import jieba
from HDYLatexParserFromDB import HDYLatexParserFromDB
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB

constdefaultname = u"test.sqlitedb"
constLogFile = u"KeyWordlogger.log"

constDicMath = u"QDbML\\AllMathTerm_ByHand.txt"
constDicTW = u'QDbReport\\dict.txt.big'

constStopWordFile = u'QDbML\\stop_words_ByHand.txt'

constListChap =  [u"不是99課綱",
                      u"跨章節試題",
                      u"B1C1數與式",
                      u"B1C2多項式函數",
                      u"B1C3指對數函數",
                      u"B2C1數列級數",
                      u"B2C2排列組合",
                      u"B2C3機率",
                      u"B2C4數據分析",
                      u"B3C1三角",
                      u"B3C2直線與圓",
                      u"B3C3平面向量",
                      u"B4C1空間向量",
                      u"B4C2空間中的平面與直線",
                      u"B4C3矩陣",
                      u"B4C4二次曲線",
                      u"B5C1機率與統計",
                      u"B5C2三角函數II",
                      u"B6C1函數與極限",
                      u"B6C2多項式函數的微積分",
                      u""
                      ]


def prepareData():
    pass

def initJiebaModule():
    jieba.set_dictionary(constDicTW)
    jieba.load_userdict(constDicMath)

def filterSpace(strItem):
    return not strItem.isspace()

def isSpecialChar(strItem):
    return strItem in u"\\{}[^~!@#$%^&*()_+]=-,$"

def isUnicodeSpecialChar(strItem):
    result = re.match(u'[\uff00-\uffef]|[\u3000 -\u303f]', strItem)
    return result is not None

def filterStopWord(truple2):
    if len(truple2[0]) == 1 :
        if isSpecialChar(truple2[0]):
            return False
        elif isUnicodeSpecialChar(truple2[0]):
            return False
        elif truple2[0] in lstStopWordFromFile:
            return False
    return True

def loadStopWordTable():
    lst = []
    with codecs.open(constStopWordFile,"r", "utf-8") as fpt:
        content = fpt.read()
        lst = content.splitlines()
    return lst

def cutString (strInput):
    lstR = filter(filterSpace, jieba.cut(strInput, cut_all=False))
    return lstR


def margeWordListIntoCountDict(dicCount, lstWord):
    for item in lstWord:
        if dicCount.has_key(item):
            dicCount[item]+=1
        else:
            dicCount[item]=1

def preProcess(strContent):
    lst = re.findall(u"\\\\begin{tikzpicture}(.*?)\\\\end{tikzpicture}", strContent, re.DOTALL)
    content = strContent
    #content = skipAllMathMode(strContent)

    lstReplaceToEmpty = [u"\\begin{QOPS}", u"\\end{QOPS}", u"\\QOP", ]

    for item in lstReplaceToEmpty:
        content = content.replace(item, u'')

    for item in lst:
        stritem = u"\\begin{tikzpicture}" + item + u"\\end{tikzpicture}"
        content = content.replace(stritem, u'tikzpicture')
    return content

def selectTop(sorted_d, nKeyWordCount = 500):
    lstTruple = sorted_d[-nKeyWordCount:]
    lstR = list(map(lambda x: x[0], lstTruple))
    return lstR

def getDataKeyWord():
    dbLatex = HDYLatexParserFromDB(constdefaultname)
    dbLatex.read()
    initJiebaModule()
    sorted_d = {}
    with codecs.open(constLogFile,"w", "utf-8") as fpt:
        nCount = dbLatex.nCountQ
        dicWordCount = {}
        for i in range(nCount):
            qPt = dbLatex.getQuestionObject(i)
            strQBODY =qPt.getQBODY()
            strContent = preProcess(strQBODY)
            margeWordListIntoCountDict (dicWordCount, cutString(strContent))

        sorted_d = sorted(dicWordCount.items(), key=operator.itemgetter(1))
        sorted_d = filter(filterStopWord, sorted_d)

        for item in sorted_d:
            fpt.write(u"%s %d %s" % (unicode(item[0]), item[1], os.linesep,))


    return sorted_d

def getKeyWordVector(strQBODY, lstKeyWord):
    lstV = []
    for item in lstKeyWord:
        if strQBODY.find(item) != -1:
            lstV.append(1)
        else:
            lstV.append(0)
    return lstV

def getMainClassType(qPt):
    nRet = len(constListChap)
    for index in range(len(constListChap)):
        if constListChap[index] in qPt.getListOfTag():
            nRet = index
            break
    return nRet


def getXYDataFromDB(lstKeyWord):
    lstYears = range(91,107)

    dbLatex = HDYLatexParserFromDB(constdefaultname)
    dbLatex.read()
    nCount = dbLatex.nCountQ

    #Find count of Row
    nRows = 0
    for i in range(nCount):
        qPt = dbLatex.getQuestionObject(i)
        if qPt.getExamYear() in lstYears:
            nRows+=1

    Xdata = np.zeros((nRows, len(lstKeyWord)))
    Ydata = np.zeros(nRows)

    nRowIndex = 0
    for i in range(nCount):
        qPt = dbLatex.getQuestionObject(i)
        if qPt.getExamYear() in lstYears:
            strQBODY = qPt.getQBODY()
            nColIndex=0

            for item in lstKeyWord:
                if strQBODY.find(item) != -1:
                    Xdata[nRowIndex,nColIndex] =1
                nColIndex+=1

            Ydata[nRowIndex] = getMainClassType(qPt)
            nRowIndex += 1
    printAInfo(Xdata)
    printAInfo(Ydata)

    from sklearn.naive_bayes import BernoulliNB
    clf = BernoulliNB()
    clf.fit(Xdata, Ydata)
    y_p = clf.predict(Xdata)
    printAInfo(y_p)
    compareResult (Ydata, y_p)
    score = clf.score(Xdata, Ydata)
    return score


def printAInfo(nparray):
    print(nparray.shape)
    print(nparray)

def compareResult(Ydata, y_p):
    nSame = 0
    nDifferent = 0
    nTotal = Ydata.shape[0]
    for index in range(nTotal):
        if Ydata[index] == y_p[index]:
            nSame+=1
        else:
            nDifferent+=1

    fResult = nSame/ (nTotal*(1.0))
    print (u"score= %f" %( fResult,))

def main():
    X = np.random.randint(2, size=(6, 100))
    Y = np.array([1, 2, 3, 4, 4, 5])
    from sklearn.naive_bayes import BernoulliNB
    clf = BernoulliNB()
    clf.fit(X, Y)
    #BernoulliNB(alpha=1.0, binarize=0.0, class_prior=None, fit_prior=True)
    print(clf.predict(X[2:3]))
    print(clf.predict_proba(X[2:3]))


lstStopWordFromFile= loadStopWordTable()

if __name__ == '__main__':
    #main()
    lstKeyWordCount = [100,200,300,400,500,600,700,800,900,1000]
    dicScore = {}
    allKeyWord = getDataKeyWord()
    for nCountKeyWord in lstKeyWordCount:
        f = getXYDataFromDB(selectTop(allKeyWord, nCountKeyWord))
        dicScore[nCountKeyWord]=f

    print(u"Words \t   Score " + os.linesep)
    for nCountKeyWord in lstKeyWordCount:
        print(u"%d \t %.02f %s" %(nCountKeyWord, dicScore[nCountKeyWord], os.linesep) )

