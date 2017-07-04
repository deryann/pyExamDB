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

        #Output message
        self.outputArea=QTextBrowser(self)
        self.outputArea.setFont(QFont ("Consolas", 14)) #設定字型

        #Show Question
        self.layoutShowQuestion = QVBoxLayout(self)
        self.outputAreaOneQuestion = QTextBrowser(self)
        self.outputAreaOneQuestion.setFont(QFont ("Consolas", 14)) #設定字型
        self.layoutShowQuestion.addWidget(self.outputAreaOneQuestion)
        self.tabBookChap = QTabWidget(self)

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
        self.layout().addLayout(self.layoutShowQuestion)
        self.layout().addLayout(self.layoutBtnsControlIndex)

        #讀取Tag 表
        self.loadTagsToNewUI()
        #self.addCheckBoxInToUI()
        self.layoutTagsPanel = QHBoxLayout()
        self.tabBookChap.setFixedWidth(400)
        self.layoutTagsPanel.addWidget(self.tabBookChap)
        self.qGroupSuggestedTag = QGroupBox( u"SuggestTags",self)
        self.layoutTagsPanel.addWidget(self.qGroupSuggestedTag)

        #增加檔案操作的按鈕
        self.btnsPanel = QVBoxLayout()
        self.btnSaveFile=QPushButton("Save", self)
        self.btnSaveFile.clicked.connect(self.onbtnSaveFileClicked)
        self.btnsPanel.addWidget(self.btnSaveFile)
        self.btnGroupTag=QPushButton("GroupingTags", self)
        self.btnGroupTag.clicked.connect(self.onbtnbtnGroupTagClicked)
        self.btnsPanel.addWidget(self.btnGroupTag)


        self.layoutTagsPanel.addLayout(self.btnsPanel)

        self.layout().addLayout(self.layoutTagsPanel)
        self.layout().addWidget(self.outputArea)


        #決定按鈕驅動事件
        self.btnFirst.clicked.connect(self.onbtnFirstClicked)
        self.btnLast.clicked.connect(self.onbtnLastClicked)
        self.btnNext.clicked.connect(self.onbtnNextClicked)
        self.btnPrev.clicked.connect(self.onbtnPrevClicked)
        self.edtIndex.textChanged.connect(self.onedtIndexChaned)


        #Data Object
        self.latex = None
        self.loadFile(u"QContent.tex")

        self.showData()
        self.showMaximized()

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
        self.outputAreaOneQuestion.setText(self.latex.getQuestion(int(self.nQIndex)))
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

    def loadTagsToNewUI(self):
        self.tabBookChap.clear()
        constStrTagFileName = u"Tag1Group.txt"
        fPt = codecs.open( constStrTagFileName, "r", "utf-8" )
        currentTab=None
        while True:
            strLine=fPt.readline()
            if strLine !=None and strLine!='':

                lst = re.findall(u"\[(.*?)\]", strLine, re.DOTALL)
                if len(lst) !=0:
                    #New 出 TAB 內頁
                    currentTab = QWidget(self)
                    currentTab.setLayout(QVBoxLayout())
                    self.tabBookChap.addTab(currentTab, lst[0])
                else:
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

        #New出所有Tag
        constStrTagFileName = u"allTags.txt"
        fPt = codecs.open( constStrTagFileName, "r", "utf-8" )
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
            self.outputArea.append("Please Input new tag string.")
        else:
            self.outputArea.append("You add New string \""+ strNewTagName +"\"" )
            self.addTagsIntoAllTags(strNewTagName)
        pass

    def onbtnNewFromClicked(self):
        strQFromName, okay=QInputDialog.getText(self, "Please input new From:", "Q From:")
        if not okay or strQFromName==u"":
            self.outputArea.append("Please Input Q from string.")
        else:
            self.outputArea.append("You add New Q From \""+ strQFromName +"\"" )
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
        self.outputArea.clear()
        self.outputArea.append(self.latex.read())
        self.outputArea.append(self.latex.getReport())
        self.outputAreaOneQuestion.clear()
        self.refreshoutputAreaOneQuestion()
        self.edtCount.setText(str(self.latex.getCountOfQ()))
        self.edtCount.setReadOnly(True)
        #self.compareQustionStrings()
        pass
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

app=QApplication(sys.argv)
testWidget=TestWidget()
testWidget.show()
sys.exit(app.exec_())