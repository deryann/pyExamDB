#coding=utf-8
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Questions Tags editor
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
from PyQt4.QtCore import *
from HDYLatexParser import HDYLatexParser
from HDYQuestionParser import HDYQuestionParser as QParser

DEFAULT_FILE_INPUT_NAME = u"Exam01All\\q106.tex"
##
# 程式所使用的常數區
#
#
const99TagFileName = u"99TagGroup.txt"
constAllStrTagFileName = u"allTags.txt"
constSuggestionTag = u"SuggestionTag.ini"

constExamStringList = [u"學測",u"指考甲",u"指考乙"]
constExamYearStringList = [u"106",u"105"]
constExamQuestionStyleStringList = [u"單選",u"多選",u"選填",u"填充",u"計算"]

class QLineEditWithDirModel(QLineEdit):
    def __init__(self,strInputName, parent):
        QLineEdit.__init__(self, strInputName, parent)
        self.completer = QCompleter()
        self.dir_model = QDirModel()
        self.completer.setModel(self.dir_model)
        self.setCompleter(self.completer)


##
# UI 呈現的程式碼
#
class QuestionTagsEditor(QWidget):
    def __init__(self):
        QWidget.__init__(self, windowTitle=u"Latex Questions Editor .")

        self.setLayout(QVBoxLayout())

        #
        # 建構編輯Tags 的暫存資料結構
        self.dicNewTagsBuffer = {}
        self.bUserAction = True

        self.layoutFileLoadUI = QHBoxLayout()
        self.edtFile = QLineEditWithDirModel(u"FileName" ,self)

        self.btnLoadFile = QPushButton (u"Load",self)
        self.layoutFileLoadUI.addWidget(self.edtFile)
        self.layoutFileLoadUI.addWidget(self.btnLoadFile)

        self.btnLoadFile.clicked.connect(self.onbtnLoadFile)

        #Design Two mode(One Question and FileMode)
        self.tabModes = QTabWidget(self)
        self.tabBookChap = QTabWidget(self)
        self.tabModeOneQuestion = QWidget(self)
        self.tabModeFilemode = QWidget(self)
        self.tabModeOneQuestion.setLayout(QVBoxLayout())

        self.tabModes.addTab(self.tabModeOneQuestion, u"Q Mode")
        self.tabModes.addTab(self.tabModeFilemode, u"File Mode")
        self.tabModes.setCurrentIndex(0)

        self.tabCustom = None
        self.prepareShowQuestionUI()
        self.prepareTagsLayout()


        self.layout().addLayout(self.layoutFileLoadUI)
        self.layout().addWidget(self.tabModes)

        self.tabModeOneQuestion.layout().addLayout(self.layoutShowQuestion)
        self.tabModeOneQuestion.layout().addLayout(self.layoutBtnTagsList)

        self.prepareIndexSettingLayout()

        self.prepareFileModeUI()

        self.tabModeOneQuestion.layout().addLayout(self.layoutTagsPanel)
        self.tabModeOneQuestion.layout().addLayout(self.layoutBtnsControlIndex)

        self.latex = None
        self.loadFile(DEFAULT_FILE_INPUT_NAME)

        self.showData()
        self.showMaximized()

        self.setupHotkey()
        self.bEditedAndNotSave = False

    def setupHotkey(self):
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_S), self), QtCore.SIGNAL('activated()'), self.onHotkeySave)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_Right), self), QtCore.SIGNAL('activated()'),
                     self.onbtnNextClicked)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_Left), self), QtCore.SIGNAL('activated()'),
                     self.onbtnPrevClicked)

    def onHotkeySave(self):
        print("[onHotkeySave]")
        self.saveUpdatedTagIntoFile()

    def prepareTagsLayout(self):
        """
        Prepare checked item for tags editing
        :return: None
        """
        self.lstCheckboxs= []
        #讀取Tag 表
        self.loadTagsToNewUI()
        self.layoutTagsPanel = QHBoxLayout()
        self.tabBookChap.setFixedWidth(500)
        self.layoutTagsPanel.addWidget(self.tabBookChap)

        #按照當下的Item 嘗試著找出一些建議的 Tageditor

        self.listwidgetForSuggestedTags = QListWidget(self)
        self.listwidgetForSuggestedTags.itemChanged.connect(self.onSuggestedItemChanged)
        self.layoutTagsPanel.addWidget(self.listwidgetForSuggestedTags)

        #增加檔案操作的按鈕

        self.btnsPanel = QVBoxLayout()
        self.btnSaveFile=QPushButton("Save", self)
        self.btnSaveFile.clicked.connect(self.onbtnSaveFileClicked)
        self.btnsPanel.addWidget(self.btnSaveFile)
        self.btnGroupTag=QPushButton("GroupingTags", self)
        self.btnGroupTag.clicked.connect(self.onbtnbtnGroupTagClicked)
        self.btnsPanel.addWidget(self.btnGroupTag)

        self.layoutTagsPanel.addLayout(self.btnsPanel)

    def prepareShowQuestionUI(self):
        self.layoutShowQuestionMetaData = QVBoxLayout(self)
        self.layoutShowQuestion = QVBoxLayout(self)
        self.layoutShowQuestionUp = QHBoxLayout(self)
        self.layoutShowQuestionMetaData = QGridLayout(self)
        self.txtOneQuestion = QTextBrowser(self)
        self.txtOneQuestion.setFont(QFont ("Consolas", 14)) #設定字型
        #self.txtOneQuestion.setFixedHeight(300)


        self.txtAns =QLineEdit("Ans" ,self)
        self.txtSol =QTextBrowser(self)
        self.reNewComboQuestionUI()

        self.comboExamYear.setFixedWidth(100)
        self.comboExam.setFixedWidth(100)
        self.comboExamQuestionStyle.setFixedWidth(100)
        self.comboExamQuestionNum.setFixedWidth(100)
        self.txtAns.setFixedWidth(100)
        self.layoutShowQuestionMetaData.addWidget(self.comboExamYear)
        self.layoutShowQuestionMetaData.addWidget(self.comboExam)
        self.layoutShowQuestionMetaData.addWidget(self.comboExamQuestionStyle)
        self.layoutShowQuestionMetaData.addWidget(self.comboExamQuestionNum)
        self.layoutShowQuestionMetaData.addWidget(self.txtAns)
        self.layoutShowQuestionUp.addWidget(self.txtOneQuestion)
        self.layoutShowQuestionUp.addLayout(self.layoutShowQuestionMetaData)
        self.layoutShowQuestion.addLayout(self.layoutShowQuestionUp)
        self.layoutShowQuestion.addWidget(self.txtSol)
        self.txtSol.setVisible(False)

        self.layoutBtnTagsList = QHBoxLayout(self)

    def removeAllWidgetsInLayout(self, layout):
        nNumDelete = layout.count()
        print (u"[removeAllWidgetsInLayout] %d" % (nNumDelete))
        for i in reversed(range(nNumDelete)):
            widgetTemp = layout.takeAt(i).widget()
            if widgetTemp in self.lstCheckboxs:
                self.lstCheckboxs.remove(widgetTemp)
            layout.removeWidget(widgetTemp)
            widgetTemp.deleteLater()
            widgetTemp = None

    def clearBtnTagsList(self):
        self.removeAllWidgetsInLayout(self.layoutBtnTagsList)

    def refreshRemoveButtonsUIforQuetionTag(self):
        self.clearBtnTagsList()
        lst = self.getLatestTagsList()
        if len(lst) == 0:
            btn = QPushButton(u"Empty Tags", self)
            btn.setEnabled(False)
            self.layoutBtnTagsList.addWidget(btn)
            return

        for item in lst :
            strButtonTitle = u"x %s" % (item)
            btn=QPushButton(strButtonTitle, self)
            btn.strCurrTag = item
            btn.clicked.connect(lambda: self.onbtnRemoveTagClicked( btn.strCurrTag))
            self.layoutBtnTagsList.addWidget(btn)
            
    def onbtnRemoveTagClicked(self, strRemoveTag):
        strMessage = "[onbtnRemoveTagClicked] %s" % (strRemoveTag)
        print (strMessage)

        self.setLatestCurrentTagsDict(strRemoveTag, Qt.Unchecked)

    def getLatestCurrentTags(self):
        if self.dicNewTagsBuffer.has_key(self.nQIndex):
            return self.dicNewTagsBuffer[self.nQIndex]
        else:
            return self.latex.getQuestionTagList(self.nQIndex)


    def setLatestCurrentTagsDict(self, strTagName, nChecked):
        """
        將輸入的標籤設定進入最新資料的暫存區
        :param strTagName: 想要輸入的標籤名
        :param nChecked: 要新增(True)，或者是移除(False)
        :return: None
        """
        print (u"[setLatestCurrentTagsDict] %s %d" %(strTagName, nChecked))
        lst = self.getLatestCurrentTags()
        lstnew= lst[:]
        if not nChecked:
            if strTagName in lst:
                lstnew.remove(strTagName)
        else:
            if strTagName not in lst:
                lstnew.append(strTagName)

        if self.isTagsListDifferent(lst,lstnew):
            self.dicNewTagsBuffer[self.nQIndex] = lstnew
            print("[setLatestCurrentTagsDict] modified")
            self.refreshTagsUI()
        else:
            print("[setLatestCurrentTagsDict] un-modified")
        print ("[self.dicNewTagsBuffer]:" +str(self.dicNewTagsBuffer) )
        self.bEditedAndNotSave = True

    def prepareIndexSettingLayout(self):
        """
        實作控制 index 決定按鈕驅動事件
        """

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
        self.btnFirst.clicked.connect(self.onbtnFirstClicked)
        self.btnLast.clicked.connect(self.onbtnLastClicked)
        self.btnNext.clicked.connect(self.onbtnNextClicked)
        self.btnPrev.clicked.connect(self.onbtnPrevClicked)
        self.edtIndex.textChanged.connect(self.onedtIndexChaned)


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

    def getLatestTagsList(self):
        if self.nQIndex in self.dicNewTagsBuffer:
            lst = self.dicNewTagsBuffer[self.nQIndex]
        else :
            lst = self.latex.getQuestionTagList(self.nQIndex)
        return lst

    def refreshoutputAreaOneQuestion(self):
        Qpt = QParser(self.latex.getQuestion(int(self.nQIndex)))
        self.txtOneQuestion.setText(Qpt.getQBODY())
        self.txtAns.setText(Qpt.getQANS())
        self.txtSol.setText(Qpt.getQSOLLISTstring())

        self.reNewCustomTagCheckItem()

        self.refreshTagsUI()

    def saveUpdatedTagIntoFile(self):
        print("[saveUpdatedTagIntoFile]")
        self.latex.saveFileWithNewTag(self.dicNewTagsBuffer)
        self.bEditedAndNotSave = False
        pass

    def refreshTagsUI(self):
        self.refreshTagCheckedUIListData()
        self.refreshRemoveButtonsUIforQuetionTag()

    def readSuggestDict(self):
        import ConfigParser
        self.configSuggestionTag = ConfigParser.ConfigParser()
        self.configSuggestionTag.readfp(codecs.open(constSuggestionTag,u"r",u"utf8"))

    def getSuggestedTags(self):
        lst = [u"不是99課綱", u"跨章節試題"]
        lstSuggest = []
        self.readSuggestDict()
        import ast
        lstSec = self.configSuggestionTag.sections()
        lstCurr = self.getLatestCurrentTags()
        for item in lstCurr:
            if item in lstSec:
                lstSuggest = ast.literal_eval(self.configSuggestionTag.get(item, u'lst'))
                lst = lst + lstSuggest
                lstSuggest = ast.literal_eval(self.configSuggestionTag.get(item, u'seclist'))
                lst = lst + lstSuggest
        return lst

    def onSuggestedItemChanged(self, widgetItem):
        print ("[onSuggestedItemChanged]"+ widgetItem.strTagName)
        if widgetItem.checkState() == QtCore.Qt.Unchecked:
            self.setLatestCurrentTagsDict( widgetItem.strTagName, False)
        elif widgetItem.checkState() == QtCore.Qt.Checked:
            self.setLatestCurrentTagsDict( widgetItem.strTagName, True)


    def refreshSuggestedTagsLayout(self):
        print("[refreshSuggestedTagsLayout]")
        lst = self.getSuggestedTags()

        for k in range(self.listwidgetForSuggestedTags.count()):
            itemWantRemoved = self.listwidgetForSuggestedTags.item(k)
            self.lstCheckboxs.remove(itemWantRemoved)

        self.listwidgetForSuggestedTags.clear()

        for item in lst:
            chkitem = QListWidgetItem(item)
            chkitem.strTagName = item
            chkitem.setFlags(chkitem.flags() | QtCore.Qt.ItemIsUserCheckable)
            chkitem.setCheckState(QtCore.Qt.Unchecked)
            self.listwidgetForSuggestedTags.addItem(chkitem)
            self.lstCheckboxs.append(chkitem)
        pass

    def refreshTagCheckedUIListData(self):
        lstTags = self.getLatestTagsList()
        if lstTags == None:
            return

        self.refreshSuggestedTagsLayout()

        for item in self.lstCheckboxs:
            if isinstance(item, QCheckBox ):
                item.setChecked(item.strTagName in lstTags)
            elif isinstance(item, QListWidgetItem):
                if item.strTagName in lstTags:
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
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
        #TODO: Move out this ThisQ function 
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


        self.refreshRemoveButtonsUIforQuetionTag()
        
    #TODO:
    def isExistedInCustomTags(self, item):
        bReturn = False
        pass

    def onChkitemStateChange(self, state):
        #透過使用者對於UI的操作才需要重新跑過的
        print("[onChkitemStateChange]")
        sender = self.sender()
        if state == Qt.Unchecked:
            self.setLatestCurrentTagsDict(sender.strTagName ,False)
        else:
            self.setLatestCurrentTagsDict(sender.strTagName, True)

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

    def closeEvent(self, event):
        print ("[closeEvent]")
        if self.bEditedAndNotSave:
            self.runSaveDialogBeforeClosed(event)

    def runSaveDialogBeforeClosed(self, closeEvent):
        strMsg = u"Are you sure you want to exit the program? \n" \
                 u"(Yes\\Save and Yes\\No)"
        reply = QtGui.QMessageBox.question(self, u'Message',
                                           strMsg, QtGui.QMessageBox.Save, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Save:
            self.saveUpdatedTagIntoFile()
            closeEvent.accept()
        elif reply == QtGui.QMessageBox.Yes:
            closeEvent.accept()
        else:
            closeEvent.ignore()
        pass

app=QApplication(sys.argv)
QuestionEditor=QuestionTagsEditor()

QuestionEditor.show()
sys.exit(app.exec_())