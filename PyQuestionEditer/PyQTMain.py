#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      USER
#
# Created:     08/08/2015
# Copyright:   (c) USER 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, re, codecs
import difflib
from PyQt4.Qt import Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, SIGNAL

from PyQt4.QtGui import *
from HDYLatexParser import HDYLatexParser
from HDYQuestionParser import HDYQuestionParser as QParser


##
# 程式所使用的常數區
#
#
const99TagFileName = u"99TagGroup.txt"
constAllStrTagFileName = u"allTags.txt"

constExamStringList = [u"學測",u"指考甲",u"指考乙"]
constExamYearStringList = [u"106",u"105"]
constExamQuestionStyleStringList = [u"單選",u"多選",u"選填",u"填充",u"計算"]

##
# UI 呈現的程式碼
#
#
class TestWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self, windowTitle=u"Latex Questions Editor .")

        self.setLayout(QVBoxLayout())

        #
        # 建構編輯Tags 的暫存資料結構
        self.dicNewTagsBuffer = {}
        self.bUserAction = True

        self.layoutFileLoadUI = QHBoxLayout()
        self.edtFile = QLineEdit("FileName" ,self)
        self.btnLoadFile = QPushButton ("Load",self)
        self.layoutFileLoadUI.addWidget(self.edtFile)
        self.layoutFileLoadUI.addWidget(self.btnLoadFile)

        self.btnLoadFile.clicked.connect(self.onbtnLoadFile)

        #Show Question
        self.layoutShowQuestion = QGridLayout(self)
        self.txtOneQuestion = QTextBrowser(self)
        self.txtOneQuestion.setFont(QFont ("Consolas", 14)) #設定字型

        self.txtAns =QLineEdit("Ans" ,self)
        self.txtSol =QTextBrowser(self)

        #


        self.reNewComboQuestionUI()
        self.layoutShowQuestion.addWidget(self.txtOneQuestion, 1,0, 1,5)

        self.layoutShowQuestion.addWidget(self.comboExamYear,2,0)
        self.layoutShowQuestion.addWidget(self.comboExam,2,1)
        self.layoutShowQuestion.addWidget(self.comboExamQuestionStyle,2,2)
        self.layoutShowQuestion.addWidget(self.comboExamQuestionNum,2,3)
        self.layoutShowQuestion.addWidget(self.txtAns,2,4)
        self.layoutShowQuestion.addWidget(self.txtSol,3,0,3,5)


        #Design Two mode(One Question and FileMode)
        self.tabModes = QTabWidget(self)
        self.tabBookChap = QTabWidget(self)
        self.tabModeOneQuestion = QWidget(self)
        self.tabModeFilemode = QWidget(self)
        self.tabModeOneQuestion.setLayout(QVBoxLayout())

        self.tabModes.addTab(self.tabModeOneQuestion, u"Q Mode")
        self.tabModes.addTab(self.tabModeFilemode, u"File Mode")
        self.tabModes.setCurrentIndex(1)

        self.tabCustom = None

        # 實作控制 index
        self.nQIndex = 0
        self.layoutBtnsControlIndex = QHBoxLayout()

        self.btnFirst=QPushButton("|<", self)
        self.btnPrev=QPushButton("<",self)
        self.edtIndex = QLineEdit ("1", self)
        self.edtCount = QLineEdit ("0", self)
        self.btnNext=QPushButton(">",self)
        self.btnLast=QPushButton(">|",self)

        self.layoutBtnsControlIndex.addWidget(self.btnFirst)
        self.layoutBtnsControlIndex.addWidget(self.btnPrev)
        self.layoutBtnsControlIndex.addWidget(self.edtIndex)
        self.layoutBtnsControlIndex.addWidget(self.edtCount)

        self.layoutBtnsControlIndex.addWidget(self.btnNext)
        self.layoutBtnsControlIndex.addWidget(self.btnLast)

        self.lstCheckboxs= []


        self.layout().addLayout(self.layoutFileLoadUI)
        self.layout().addWidget(self.tabModes)
        self.tabModeOneQuestion.layout().addLayout(self.layoutShowQuestion)
        self.tabModeOneQuestion.layout().addLayout(self.layoutBtnsControlIndex)

        #讀取Tag 表
        self.loadTagsToNewUI()
        #self.addCheckBoxInToUI()
        self.layoutTagsPanel = QHBoxLayout()
        self.tabBookChap.setFixedWidth(600)
        self.layoutTagsPanel.addWidget(self.tabBookChap)

        #增加檔案操作的按鈕
        self.btnsPanel = QVBoxLayout()
        self.btnSaveFile=QPushButton("Save", self)
        self.btnSaveFile.clicked.connect(self.onbtnSaveFileClicked)
        self.btnsPanel.addWidget(self.btnSaveFile)
        self.btnGroupTag=QPushButton("GroupingTags", self)
        self.btnGroupTag.clicked.connect(self.onbtnbtnGroupTagClicked)
        self.btnsPanel.addWidget(self.btnGroupTag)

        self.layoutTagsPanel.addLayout(self.btnsPanel)

        self.tabModeOneQuestion.layout().addLayout(self.layoutTagsPanel)

        #決定按鈕驅動事件
        self.btnFirst.clicked.connect(self.onbtnFirstClicked)
        self.btnLast.clicked.connect(self.onbtnLastClicked)
        self.btnNext.clicked.connect(self.onbtnNextClicked)
        self.btnPrev.clicked.connect(self.onbtnPrevClicked)
        self.edtIndex.textChanged.connect(self.onedtIndexChaned)

        self.prepareFileModeUI()



        #Data Object
        self.latex = None
        self.loadFile(u"QSingleChoice.tex")

        self.showData()
        self.showMaximized()

    def prepareFileModeUI(self):
        container= self.tabModeFilemode
        container.setLayout(QVBoxLayout())
        self.txtbFile = QTextBrowser(self)
        self.txtbFile.setFont(QFont ("Consolas", 14)) #設定字型
        container.layout().addWidget(self.txtbFile)

        self.qGroupExamInfoEditor = QGroupBox( u"Add ExamInfo For All Question",self)
        self.qGroupExamInfoEditor.setLayout(QHBoxLayout())

        self.comboExamAdder = QComboBox(self)
        self.comboExamAdder.addItems(constExamStringList)
        self.comboExamYearAdder =QComboBox(self)
        self.comboExamYearAdder.addItems(constExamYearStringList)
        self.comboExamQuestionStyleAdder =QComboBox(self)
        self.comboExamQuestionStyleAdder.addItems(constExamQuestionStyleStringList)

        self.edtStart = QLineEdit(u"1" ,self)
        self.lblStart = QLabel(u"Start Label：")
        self.btnRunAddExamInfo=QPushButton(u"Run",self)
        self.btnRunAddExamInfo.clicked.connect(self.onbtnRunAddExamInfoClicked)

        self.qGroupExamInfoEditor.layout().addWidget(self.comboExamAdder)
        self.qGroupExamInfoEditor.layout().addWidget(self.comboExamYearAdder)
        self.qGroupExamInfoEditor.layout().addWidget(self.comboExamQuestionStyleAdder)
        self.qGroupExamInfoEditor.layout().addWidget(self.lblStart)
        self.qGroupExamInfoEditor.layout().addWidget(self.edtStart)
        self.qGroupExamInfoEditor.layout().addWidget(self.btnRunAddExamInfo)

        container.layout().addWidget(self.qGroupExamInfoEditor)

    def onbtnRunAddExamInfoClicked(self):
        """
        對檔案中的每一個題目，執行新增ExamInfo 的工作
        """
        strExamAdder = self.comboExamAdder.currentText()
        strExamYearAdder = self.comboExamYearAdder.currentText()
        strExamQuestionStyleAdder =self.comboExamQuestionStyleAdder.currentText()
        print(strExamYearAdder+strExamAdder+strExamQuestionStyleAdder)
        strStartNum = self.edtStart.text()
        self.latex.setExamInfoForAllQuestions(strExamYearAdder,strExamAdder,strExamQuestionStyleAdder,strStartNum)
        self.showData()


    def reNewComboQuestionUI(self):
        self.comboExam = QComboBox(self)
        self.comboExamYear =QComboBox(self)
        self.comboExamQuestionStyle =QComboBox(self)
        self.comboExamQuestionNum =QComboBox(self)

    def onLeftKey(self):
        print("[onLeftKey]")
        pass

    def onbtnbtnGroupTagClicked(self):
        print("onbtnbtnGroupTagClicked")
        self.testOupoutGroupingSelectedTags()

    def onbtnSaveFileClicked(self):
        print("onbtnSaveFileClicked")
        self.saveUpdatedTagIntoFile( )
        pass

    def onbtnLoadFile(self):
        strfileName = QFileDialog.getOpenFileName(self, u"Open HDY Latex", ".", u"Tex Files (*.tex )")
        print ("fileName:" +strfileName)
        self.loadFile(strfileName)
        pass

    def loadFile(self, strfileName):
        self.edtFile.setText(strfileName)
        self.latex = HDYLatexParser(strfileName)
        self.showData()

    def onedtIndexChaned(self, strText):
        try:
            nIndex= int (strText) -1
        except:
            nIndex=self.nQIndex
            pass
        self.nQIndex=nIndex
        self.refreshoutputAreaOneQuestion()
        print("onedtIndexChaned")
        pass

    def refreshoutputAreaOneQuestion(self):
        Qpt = QParser(self.latex.getQuestion(int(self.nQIndex)))
        self.txtOneQuestion.setText(Qpt.getQBODY())
        self.txtAns.setText(Qpt.getQANS())
        self.txtSol.setText(Qpt.getQSOL())

        self.reNewCustomTagCheckItem()
        #確認是否有更新版Tag List *
        if self.nQIndex in self.dicNewTagsBuffer:
            lst = self.dicNewTagsBuffer[self.nQIndex]
        else :
            lst = self.latex.getQuestionTagList(self.nQIndex)
        self.bUserAction = False
        self.refreshTagListData(lst)
        self.bUserAction = True

    def saveUpdatedTagIntoFile(self):
        print("saveUpdatedTagIntoFile")
        self.latex.saveNewFileWithNewTag(self.dicNewTagsBuffer)
        pass

    def refreshTagListData(self, lstTags):
        if lstTags == None:
            return

        for item in self.lstCheckboxs:
            item.setChecked(item.strTagName in lstTags)
            pass

    def setCurrentIndex(self, nIndex):
        if nIndex < self.latex.getCountOfQ() and nIndex >= 0:
            self.nQIndex = nIndex
            #事實上，秀出來的Index 是由 1 開始的
            self.edtIndex.setText(str(self.nQIndex+1))

    def onbtnFirstClicked(self):
        self.setCurrentIndex(0)

    def onbtnLastClicked(self):
        self.setCurrentIndex(self.latex.getCountOfQ()-1)

    def onbtnNextClicked(self):
        self.setCurrentIndex(self.nQIndex +1)

    def onbtnPrevClicked(self):
        self.setCurrentIndex(self.nQIndex -1)

    def addCheckBoxInToUI(self):
        pass

    def prepare99TagsUI(self):
        """
        準備所有99課綱章節的Tags UI (GridLayout)
        """
        fPt = codecs.open( const99TagFileName, "r", "utf-8" )
        currentTab = QWidget(self)
        currentGrid = QGridLayout(self)
        currentTab.setLayout(currentGrid)
        self.tabBookChap.addTab(currentTab, u"99課綱Tag")
        nCurrentRow =0
        nCurrentCol =0
        while True:
            strLine=fPt.readline()
            if strLine !=None and strLine!='':
                lst = re.findall(u"\[(.*?)\]", strLine, re.DOTALL)
                if len(lst) !=0:
                    nCurrentRow +=1
                    nCurrentCol =0
                else:
                    lst = re.findall(u"QTAG{(.*?)}", strLine, re.DOTALL)
                    if len(lst) !=0:
                        strNew = lst[0]
                        chkitem = QCheckBox(strNew,self)
                        chkitem.strTagName=strNew
                        chkitem.stateChanged.connect(self.onChkitemStateChange)
                        self.lstCheckboxs.append(chkitem)
                        currentGrid.addWidget(chkitem, nCurrentRow, nCurrentCol)
                        nCurrentCol+=1
            else:
                break


    def loadTagsToNewUI(self):
        self.tabBookChap.clear()
        self.prepare99TagsUI()
                #New出所有Tag

        fPt = codecs.open( constAllStrTagFileName, "r", "utf-8" )
        currentTab=None
        #New 出 AllTAB 內頁
        currentTab = QWidget(self)
        currentTab.setLayout(QVBoxLayout())
        self.tabBookChap.addTab(currentTab, u"all")
        while True:
            strLine=fPt.readline()
            if strLine !=None and strLine!='':
                lst = re.findall(u"QTAG{(.*?)}", strLine, re.DOTALL)
                if len(lst) !=0:
                    strNew = lst[0]
                    chkitem = QCheckBox(strNew,self)
                    chkitem.strTagName=strNew
                    chkitem.stateChanged.connect(self.onChkitemStateChange)
                    self.lstCheckboxs.append(chkitem)
                    currentTab.layout().addWidget(chkitem)
            else:
                break
        self.tabCustom=QWidget(self)
        self.tabBookChap.addTab(self.tabCustom, u"ThisQ")
        self.tabCustom.setLayout(QVBoxLayout())
        self.newUIforEditTag()
        pass

    ##
    # 當題目裡面存在有App 沒有包含的 QTAG 也必須列出他的UI
    #
    def reNewCustomTagCheckItem(self):
        lst = self.latex.getQuestionTagList(self.nQIndex)
        for item in lst :
            if not self.isExistedInCustomTags(item):
                chkitem = QCheckBox(item,self)
                chkitem.strTagName=item
                chkitem.stateChanged.connect(self.onChkitemStateChange)
                self.lstCheckboxs.append(chkitem)
                self.tabCustom.layout().addWidget(chkitem)

    #TODO:
    def isExistedInCustomTags(self, item):
        bReturn = False
##        for item in self.tabCustom.layout():
##            pass
        pass

    def onChkitemStateChange(self, state):
        #透過使用者對於UI的操作才需要重新跑過的
        if self.bUserAction:
            self.saveCurrentQuestionTagStatusFromUI()

    def saveCurrentQuestionTagStatusFromUI(self):
        print ("saveCurrentQuestionTagStatusFromUI")
        lst =[]
        for item in self.lstCheckboxs:
            if item.isChecked():
                lst.append(item.strTagName )
            pass
        if self.isTagsListDifferent(lst, self.latex.getQuestionTagList(self.nQIndex)):
            self.dicNewTagsBuffer[self.nQIndex] = lst
        print ("self.dicNewTagsBuffer:")
        print (str(self.dicNewTagsBuffer))

    def isTagsListDifferent(self, lst1, lst2):
        if len(lst1) != len(lst2):
            bDifferent = True
        else:
            bDifferent = False
            for item in lst1:
                if item in lst2:
                    continue
                else:
                    bDifferent = True
                    break
        return bDifferent

    def newUIforEditTag(self):
        #New 出 EditTag 內頁
        currentTab = QWidget(self)
        currentTab.setLayout(QVBoxLayout())
        self.tabBookChap.addTab(currentTab, u"edit")
        self.btnNewTag=QPushButton("New Tag",self)
        self.btnNewTag.clicked.connect(self.onbtnNewTagClicked)
        self.btnNewFrom=QPushButton("New Q From" ,self)
        self.btnNewFrom.clicked.connect(self.onbtnNewFromClicked)
        currentTab.layout().addWidget(self.btnNewTag)
        currentTab.layout().addWidget(self.btnNewFrom)

        pass

    def onbtnNewTagClicked(self):
        strNewTagName, okay=QInputDialog.getText(self, "Please input new tage:", "New Tag String:")
        if not okay or strNewTagName==u"":
            self.dprint("Please Input new tag string.")
        else:
            self.dprint("You add New string \""+ strNewTagName +"\"" )
            self.addTagsIntoAllTags(strNewTagName)
        pass

    def dprint(self, txt ):
        print(txt)

    def onbtnNewFromClicked(self):
        strQFromName, okay=QInputDialog.getText(self, "Please input new From:", "Q From:")
        if not okay or strQFromName==u"":
            self.dprint("Please Input Q from string.")
        else:
            self.dprint("You add New Q From \""+ strQFromName +"\"" )
            strfileName =QFileDialog.getSaveFileName(self, u"Save HDY Latex", ".", u"Tex Files (*.tex )")
            self.addQFromIntoAllQuestions(strQFromName, strfileName)
        pass

    def addQFromIntoAllQuestions(self, strQFromName, strfileName):
        self.latex.setFromTagToAllQuestions(strQFromName, strfileName)
        pass

    def addTagsIntoAllTags(self,strNewTag):
        #1.讀入所有tags
        #New出所有Tag
        constStrTagFileName = u"allTags.txt"
        fPt = codecs.open( constStrTagFileName, "r", "utf-8" )
        lstTags = []
        while True:
            strLine=fPt.readline()
            if strLine !=None and strLine!='':
                lst = re.findall(u"QTAG{(.*?)}", strLine, re.DOTALL)
                lstTags += lst
            else:
                break

        if not strNewTag in lstTags:
            fPt = codecs.open( constStrTagFileName, "a+", "utf-8" )
            strInput = os.linesep + u"\\QTAG{" + strNewTag + u"}"
            fPt.write(strInput)
            fPt.close()
            #重新整理Tag UI
            self.loadTagsToNewUI()
        else:
            print ("檔案裡面已經有這個Tag了!!")

        #3.存入新檔案
        print (str(lstTags))
        pass

    def showData(self):
        self.dprint(self.latex.read())
        self.dprint(self.latex.getReport())
        self.txtOneQuestion.clear()
        self.txtAns.clear()
        self.txtSol.clear()
        self.refreshoutputAreaOneQuestion()
        self.edtCount.setText(str(self.latex.getCountOfQ()))
        self.edtCount.setReadOnly(True)

        self.showDataInFileMode()
        pass

    def showDataInFileMode(self):
        self.txtbFile.clear()
        self.txtbFile.setText(self.latex.read())

    ##
    # 測試兩個問題字串的相似度
    #
    def compareQustionStrings (self):
        nQcount = self.latex.getCountOfQ()
        for i in range(0, nQcount):
            for j in range(0, nQcount):
                strNum = str(i) + " - " + str (j)
                print (strNum)
                strA =self.latex.getQuestion(i)
                strB =self.latex.getQuestion(j)
                print (difflib.SequenceMatcher(None, strA, strB).ratio())

    ##
    # 篩選想要的 Tags 與排序進入新檔案
    #
    def testOupoutGroupingSelectedTags(self):
        strOutPutFileName = u"GroupingTagsOutput.tex"
        lstSelectedTags = [ u"B1C1數與式",u"B1C2-1", u"B1C2-2", u"B1C2-3", u"B1C2-4", u"B1C3-1", u"B1C3-2"]
        self.latex.saveNewFileWithSelectedTag(strOutPutFileName, lstSelectedTags)
        pass

def generateTexFileTemplate():
    """
    利用無引數的物件，按照指定的題數做出空白的檔案來
    """
    strYear="105"
    strExam="學測"
    lstQstyle = [["單選","1","6"],["多選","7","13"],["選填","A","G"] ]
    strOutFileName = "105.tex"
    latexPt = HDYLatexParser(None)
    latexPt.newTemplate(strYear, strExam, lstQstyle, "105.tex")

def generateTexFileTemplateByCSVFile():
    """
    另用已經有的csv資料寫出Tex file
    """
    import pandas as pd
    strFileName= u"E:\\NCTUG2\\Code\\pyExamDBF5\\PyQuestionEditer\\exam_xc.csv"
    lstUsecols = [u'類別',u'年份',u'題型',u'題號',u'答案',u'章節', u'章節（短）',
        u'P',u'Ph',u'Pm',u'Pl',u'P90',u'P70',u'P50',u'P30',u'P10',u'T',u'D',u'D1',u'D2',u'D3',u'D4',
        u'TA',u'TB',u'TC',u'TD',u'TE',u'HA',u'HB',u'HC',u'HD',u'HE',u'LA',u'LB',u'LC',u'LD',u'LE']
    exam = pd.read_csv(strFileName, encoding = 'utf8',usecols = lstUsecols)

    print(exam[exam[u'年份']==106])
    latexPt = HDYLatexParser(None)
    latexPt.newTemplateByCsvInput(exam)

#generateTexFileTemplate()   #測試自動生成 Tex 模板樣式
#generateTexFileTemplateByCSVFile()

app=QApplication(sys.argv)
testWidget=TestWidget()

testWidget.show()
sys.exit(app.exec_())