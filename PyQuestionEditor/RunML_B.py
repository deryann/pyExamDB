# -*- coding: utf-8 -*-
import codecs
import operator
import os
import re
import pickle

import jieba
import numpy as np

from HDYLatexParserFromDB import HDYLatexParserFromDB
from sklearn.naive_bayes import BernoulliNB
from sklearn.model_selection import train_test_split

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
                      u"未分類"
                      ]

lstStopWordFromFile = []
constKeyWordCacheFileNameOutputFilePath = u"KeywordCache.pickle"

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
    """
    將字串做一些斷詞前的前處理
    :param strContent: 輸入的字串
    :return:
    """
    lst = re.findall(u"\\\\begin{tikzpicture}(.*?)\\\\end{tikzpicture}", strContent, re.DOTALL)
    content = strContent

    lstReplaceToEmpty = [u"\\begin{QOPS}", u"\\end{QOPS}", u"\\QOP", ]

    for item in lstReplaceToEmpty:
        content = content.replace(item, u'')

    for item in lst:
        stritem = u"\\begin{tikzpicture}" + item + u"\\end{tikzpicture}"
        content = content.replace(stritem, u'tikzpicture')
    return content

def selectTop(sorted_d, nKeyWordCount = 500):
    """
    選擇個數由大到小的前 (nKeyWord) 個，並且只保留字串部分，丟棄個數部分
    :param sorted_d: A list of truple ("字串", 個數) 排序方式由"個數"由小到大
    :param nKeyWordCount:
    :return:
    """
    lstTruple = sorted_d[-nKeyWordCount:]
    lstR = list(map(lambda x: x[0], lstTruple))
    return lstR

def isDataKeyWordFromCacheFile():
    return os.path.isfile(constKeyWordCacheFileNameOutputFilePath)

def loadDataKeyWordFromCacheFile():
    itemlist=[]
    with open(constKeyWordCacheFileNameOutputFilePath, 'rb') as fp:
        itemlist = pickle.load(fp)
    return itemlist

def getDataKeyWord():
    """
    產生想要的 KeyWord Table
    :return: A list of truple ("字串", 個數) 排序方式由"個數"由小到大
    """
    if isDataKeyWordFromCacheFile():
        print("[getDataKeyWord] load by Cache File.")
        sorted_d = loadDataKeyWordFromCacheFile()
    else:
        print("[getDataKeyWord] load by runing.")
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


        with open(constKeyWordCacheFileNameOutputFilePath, 'wb') as fp:
            pickle.dump(sorted_d, fp)

    return sorted_d


def getMainClassType(qPt, dicParam = {} ):
    """
    對題目做出主要類型的編號
    :param qPt:
    :param dicParam:
    :return:
    """
    nRet = 0
    if dicParam.has_key(u"checkClass"):
        nRet = 0
        return get2MainClass(qPt, dicParam[u"checkClass"])
    else:
        nRet = len(constListChap) - 1
        for index in range(len(constListChap)):
            if constListChap[index] in qPt.getListOfTag():
                nRet = index
                break
    return nRet

def get2MainClass(qPt, strWantClassWord):
    """
    測試想要的 tag 有或者是沒有
    :param qPt:
    :param strWantClassWord:
    :return:
    """
    nRet = 0
    if strWantClassWord in qPt.getListOfTag():
        nRet = 1
    return nRet


def getMType(qPt, dicParams={}):
    """
    對題目做出主要類型的編號
    :param qPt:
    :return:
    """
    nRet = 0

    if u"B1C1數與式" in qPt.getListOfTag():
        nRet = 1
    return nRet

def getXYDataFromDB(lstKeyWord, funClassType=getMainClassType, dicParams = {}):
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
                    Xdata[nRowIndex, nColIndex] =1
                nColIndex+=1

            Ydata[nRowIndex] = funClassType(qPt, dicParams)
            nRowIndex += 1
    return Xdata, Ydata

def trainingByalg(Xdata, Ydata, clf = BernoulliNB()):
    clf.fit(Xdata, Ydata)
    y_p = clf.predict(Xdata)
    score = clf.score(Xdata, Ydata)
    return score


def printAInfo(nparray):
    print(nparray.shape)
    print(nparray)

def compareResult(Ydata, y_p):
    """
    比較Ydata 跟 預測的 y_p 每個Level 的 Error Rate
    :param Ydata:
    :param y_p:
    :return:
    """
    nSame = 0
    nDifferent = 0
    nTotal = Ydata.shape[0]
    aClassErrorCount = np.zeros(len(constListChap))
    aClassTotalCount = np.zeros(len(constListChap))

    for index in range(nTotal):
        nClass = int(Ydata[index])
        aClassTotalCount[nClass]+=1
        if Ydata[index] == y_p[index]:
            nSame+=1
        else:
            aClassErrorCount[nClass] += 1
            nDifferent+=1

    fResult = nSame/ (nTotal*(1.0))

    print (u"score= %f" %( fResult,))
    for index in range(len(constListChap)):
        fClassErrorRate = aClassErrorCount[index] / aClassTotalCount[index]*1.0
        print (u"Class %d %s Error Rate = %.02f (%d/%d)" % (index, constListChap[index], fClassErrorRate, aClassErrorCount[index],
                                                             aClassTotalCount[index]))


def showComparsionWithKeyWordNumber():
    lstKeyWordCount = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    dicScore = {}
    allKeyWord = getDataKeyWord()
    for nCountKeyWord in lstKeyWordCount:
        Xdata, Ydata = getXYDataFromDB(selectTop(allKeyWord, nCountKeyWord), getMType)

        f = trainingByalg(Xdata, Ydata)
        dicScore[nCountKeyWord] = f

    print(u"Words \t   Score " + os.linesep)
    for nCountKeyWord in lstKeyWordCount:
        print(u"%d \t %.02f %s" % (nCountKeyWord, dicScore[nCountKeyWord], os.linesep))

def show2ClassML():
    """
    針對每一個Class 只做"是" "否" 的判別，並且計算其錯誤率
    :return:
    """
    nAllClasscount = len(constListChap)
    nCountKeyWord=1000
    dicScore = {}
    allKeyWord = getDataKeyWord()
    for index in range(nAllClasscount):
        item = constListChap[index]
        Xdata, Ydata = getXYDataFromDB(selectTop(allKeyWord, nCountKeyWord), getMainClassType, dicParams={u"checkClass":item})
        X_train, X_test, y_train, y_test = train_test_split(Xdata, Ydata, test_size=0.25, random_state=42)

        clf = BernoulliNB()
        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)

        dicScore[index] = score

    print(u"Words \t   Score ")

    for index in range(nAllClasscount):
        print(u"%s \t %.02f" % (constListChap[index], dicScore[index]))



if __name__ == '__main__':
    lstStopWordFromFile = loadStopWordTable()
    show2ClassML()


