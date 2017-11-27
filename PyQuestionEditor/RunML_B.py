# -*- coding: utf-8 -*-
import codecs
import operator
import os,sys
import re
import pickle
import timeit

import jieba
import numpy as np

from HDYLatexParserFromDB import HDYLatexParserFromDB
from sklearn.naive_bayes import BernoulliNB
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.metrics import f1_score, recall_score, precision_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import export_graphviz
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

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
                      # u"B5C1機率與統計",
                      # u"B5C2三角函數II",
                      # u"B6C1函數與極限",
                      # u"B6C2多項式函數的微積分",
                      # u"未分類"
                      ]
constWorkPath = u"E:\\NCTUG2\\Code\\pyExamDBDevUI\\PyQuestionEditor"
lstStopWordFromFile = []
constKeyWordCacheFileNameOutputFilePath = u"KeywordCache.pickle"

constClassifierAgents = u"ClassifierAgents.pickle"

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

def getListOfAllKeyWord():
    """
    產生想要的 KeyWord Table
    :return: A list of truple ("字串", 個數) 排序方式由"個數"由小到大
    """
    if isDataKeyWordFromCacheFile():
        print("[getListOfAllKeyWord] load by Cache File.")
        sorted_d = loadDataKeyWordFromCacheFile()
    else:
        print("[getListOfAllKeyWord] load by runing.")
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

def getCurrentXDataKeyWord():
    with open(constXDataKeyWord, "rb") as fp:
        lstKeyWord = pickle.load(fp)
    return lstKeyWord

def getOneXData(qPt, nCountKeyword, allKeyWords=None):
    """
    從問題當中，找出 Xdata 向量
    :param qPt:
    :return:
    """
    if allKeyWords is None:
        allKeyWords = getListOfAllKeyWord()
    lstKeyWord = selectTop(allKeyWords, nCountKeyword)
    Xdata = np.zeros((1, len(lstKeyWord)))
    strQBODY = qPt.getQBODY()
    nColIndex=0
    for item in lstKeyWord:
        if strQBODY.find(item) != -1:
            Xdata[0, nColIndex] = 1
        nColIndex += 1
    return Xdata


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
    lstKeyWordCount = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,2000,3000]
    dicScore = {}
    allKeyWord = getListOfAllKeyWord()

    for nCountKeyWord in lstKeyWordCount:
        currentKeyWord = selectTop(allKeyWord, nCountKeyWord)
        Xdata, Ydata = getXYDataFromDB(currentKeyWord, getMType)

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
    allKeyWord = getListOfAllKeyWord()
    currentKeyWord = selectTop(allKeyWord, nCountKeyWord)
    for index in range(nAllClasscount):
        item = constListChap[index]
        Xdata, Ydata = getXYDataFromDB(currentKeyWord, getMainClassType, dicParams={u"checkClass":item})
        X_train, X_test, y_train, y_test = train_test_split(Xdata, Ydata, test_size=0.25, random_state=42)

        clf = BernoulliNB()
        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)

        dicScore[index] = score

    print(u"Words \t   Score ")

    for index in range(nAllClasscount):
        print(u"%s \t %.02f" % (constListChap[index], dicScore[index]))

def show2ClassMLByAllClassifiers ():
    lstClassifiers = [
        BernoulliNB(),
        GaussianNB(),
        KNeighborsClassifier(3),
        SVC(kernel="linear", C=0.025),
        SVC(gamma=2, C=1),
        DecisionTreeClassifier(max_depth=5),
        RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
        AdaBoostClassifier()]
    names = ["Basic Naive Bayes", "GaussianNB",
        "Nearest Neighbors", "Linear SVM", "RBF SVM", "Decision Tree",
             "Random Forest", "AdaBoost",
             ]

    nAllClasscount = len(constListChap)

    nAllClassifiers = len(lstClassifiers)
    dicScore = np.zeros((nAllClasscount, nAllClassifiers))
    allKeyWord = getListOfAllKeyWord()
    nCountKeyWord = len(allKeyWord)
    currentKeyWord = selectTop(allKeyWord, nCountKeyWord)

    for index in range(nAllClasscount):
        print( constListChap[index])
        item = constListChap[index]
        Xdata, Ydata = getXYDataFromDB(currentKeyWord, getMainClassType, dicParams={u"checkClass":item})
        X_train, X_test, y_train, y_test = train_test_split(Xdata, Ydata, test_size=0.50, random_state=10)
        for clfIndex in range(nAllClassifiers):
            print (names[clfIndex])
            clf = lstClassifiers[clfIndex]
            clf.fit(X_train, y_train)
            clf.strTagName = item
            y_pre = clf.predict(X_test)
            dicScore[index, clfIndex] = f1_score(y_test, y_pre)


    strheader = u"Words," + u",".join(names)
    print(strheader)


    for index in range(nAllClasscount):
        strRow = constListChap[index]
        for clfIndex in range(nAllClassifiers):
            strRow += u", %.02f" %( dicScore[index, clfIndex],)
        print (strRow)

def loadClassifierAgent(bDrawDTreePNG=False):

    with open(constClassifierAgents, 'rb') as fp:
        agents = pickle.load(fp)

    #Draw DT picture
    if bDrawDTreePNG:
        nIndex = 0
        for clf in agents:
            mainFileName = u"DTreeAgent%02d" % (nIndex,)
            filename = mainFileName+u".dot"
            allKeyWord = getListOfAllKeyWord()
            currentKeyWord = selectTop(allKeyWord, clf.nKeyWord)
            wordtable =[]
            for item in currentKeyWord:
                wordtable.append( item.encode("utf8"))
            export_graphviz(clf, out_file = filename, feature_names = wordtable)
            postModifyDOT(filename)
            toPNG(mainFileName)
            print(u"%s score = %.02f" % (clf.strTagName, clf.ff1))
            nIndex+=1

    return agents

def toPNG(mainFileName):
    """
    將 DOT 圖檔轉換成 PNG 檔
    :param mainFileName:
    :return:
    """
    os.chdir(constWorkPath)
    cmdlist = [#u'dot -Tps %.dot -o %.ps',
               u'dot -Tpng %.dot -o %.png'
               ]
    for strTemplate in cmdlist:
        timer_start = timeit.default_timer()
        strCmd = strTemplate.replace(u'%', mainFileName)
        os.system(strCmd.encode(sys.getfilesystemencoding()))
        timer_end = timeit.default_timer()
        print("Time usage:", timer_end - timer_start, " sec(s)")
        print (strCmd+ u" Completed!!")


def postModifyDOT(filename):
    """
    更動自動產生的DOT檔案，加入中文字型名稱。
    :param filename:
    :return:
    """
    strAll =''
    with codecs.open(filename, 'r',encoding="utf8") as pt:
        strAll = pt.read()
    strAll = strAll.replace(u"node [shape=box] ;",u"node [shape=box, fontname = \"PMingLiu\"] ;")
    with codecs.open(filename, 'w',encoding="utf8") as pt:
        pt.write(strAll)


def doAbestDTree():
    """
    測試各項features 參數 對各決策樹的影響 並且記錄 ff1 score 最好的!
    :return:
    """
    lstD = [3,4,5,6,7,8]
    lstCountKeyWord =[1000,2000,3000]
    lstCriterion = ["gini", "entropy"]

    nAllClasscount = len(constListChap)
    lstClassifierAgent = []
    for index in range(nAllClasscount):
        fMax = -1.0
        lstClassifierAgent.append(None)
        strTagName = constListChap[index]
        for strCriterion in lstCriterion:
            for d in lstD:
                for nCount in lstCountKeyWord:
                    clf = DTreeMode(strTagName, nCount, d, strCriterion )
                    if clf.ff1 > fMax:
                        fMax = clf.ff1
                        lstClassifierAgent[index]=clf
    for item in lstClassifierAgent:
        print (u"%s \t strCriterion=%s \tC=%d\tD=%d\tff1=%.02f" % (item.strTagName, item.strCriterion ,item.nKeyWord, item.nLeveldepth, item.ff1))
    #save agent to pickle
    with open(constClassifierAgents, 'wb') as fp:
        pickle.dump(lstClassifierAgent, fp)


def DTreeMode(strTagName=u'', nCountKeyWord= 2000, Level_depth =3, strCriterion = 'gini' ):

    allKeyWord = getListOfAllKeyWord()
    lstClassifierAgent = []
    currentKeyWord = selectTop(allKeyWord, nCountKeyWord)
    print (u"DESC : Decision Tree Params level=%d nCountKeyWord=%d" % (Level_depth, nCountKeyWord))

    # Dump current KeyWord
    # with open(constXDataKeyWord, "wb") as fp:
    #     pickle.dump(currentKeyWord, fp )

    #for index in range(nAllClasscount):
    clf = DecisionTreeClassifier(criterion=strCriterion,  max_depth=Level_depth)

    Xdata, Ydata = getXYDataFromDB(currentKeyWord, getMainClassType,
                                   dicParams={u"checkClass": strTagName})
    X_train, X_test, y_train, y_test = train_test_split(Xdata, Ydata, test_size=0.5, random_state=0)
    clf.fit(X_train, y_train)
    clf.strTagName = strTagName
    clf.nKeyWord = nCountKeyWord
    clf.nLeveldepth = Level_depth

    y_pred_class = clf.predict(X_test)
    clf.fRecall = recall_score(y_test, y_pred_class)
    clf.fPrecision = precision_score(y_test, y_pred_class)
    clf.ff1 = f1_score(y_test, y_pred_class)
    clf.strCriterion = strCriterion

    return clf

class Tagsuggestor:
    """
    將Machine learning 好的分類器與字串庫讀入 並暫存
    """
    def __init__(self):
        self.allKeyWord = getListOfAllKeyWord()
        self.agentsMLTags = loadClassifierAgent()

    def getSuggestionTags(self, qPt):
        lst = []
        #getXData for qPt
        for clf in self.agentsMLTags:
            XData = getOneXData(qPt, clf.nKeyWord, self.allKeyWord)
            y = clf.predict(XData)
            if y[0] != 0.0:
                lst.append(clf.strTagName)
        if len(lst)!= 0:
            print (u'ML Tags: %s' % ( ",".join(lst),))
        return lst

if __name__ == '__main__':
    lstStopWordFromFile = loadStopWordTable()
    #show2ClassML()
    #show2ClassMLByAllClassifiers()
    #loadClassifierAgent()
    doAbestDTree()
    loadClassifierAgent()