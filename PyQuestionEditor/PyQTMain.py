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
from HDYLatexParser import HDYLatexParser
from HDYQuestionParser import HDYQuestionParser as QParser

DEFAULT_FILE_INPUT_NAME = u"Exam01All\\q106.tex"
##
# 程式所使用的常數區
#
#
const99TagFileName = u"99TagGroup.txt"
constAllStrTagFileName = u"allTags.txt"

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

        self.prepareIndexSettingLayout()

        self.prepareFileModeUI()

        self.tabModeOneQuestion.layout().addLayout(self.layoutTagsPanel)
        self.tabModeOneQuestion.layout().addLayout(self.layoutBtnsControlIndex)

        self.latex = None
        self.loadFile(DEFAULT_FILE_INPUT_NAME)

        self.showData()
        self.showMaximized()

    def prepareTagsLayout(self):
        self.lstCheckboxs= []
        #讀取Tag 表
        self.loadTagsToNewUI()
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

    def prepareShowQuestionUI(self):
        self.layoutShowQuestion = QGridLayout(self)
        self.txtOneQuestion = QTextBrowser(self)
        self.txtOneQuestion.setFont(QFont ("Consolas", 14)) #設定字型

        self.txtAns =QLineEdit("Ans" ,self)
        self.txtSol =QTextBrowser(self)
        self.reNewComboQuestionUI()
        self.layoutShowQuestion.addWidget(self.txtOneQuestion, 1,0, 1,5)

        self.layoutShowQuestion.addWidget(self.comboExamYear,2,0)
        self.layoutShowQuestion.addWidget(self.comboExam,2,1)
        self.layoutShowQuestion.addWidget(self.comboExamQuestionStyle,2,2)
        self.layoutShowQuestion.addWidget(self.comboExamQuestionNum,2,3)
        self.layoutShowQuestion.addWidget(self.txtAns,2,4)
        self.layoutShowQuestion.addWidget(self.txtSol,3,0,3,5)
        self.addQuestionTagsList()
        
        
    def addQuestionTagsList(self):
        self.btnTagsList = QHBoxLayout()
        self.tabModeOneQuestion.layout().addLayout(self.btnTagsList)
        
    def clearBtnTagsList(self):
        layout = self.btnTagsList
        nNumDelete = layout.count()
        print (u"[clearBtnTagsList] %d" %(nNumDelete) )
        for i in reversed(range(nNumDelete)):
            widgetTemp = layout.takeAt(i).widget()
            layout.removeWidget(widgetTemp)
            widgetTemp.deleteLater()
            widgetTemp = None

    def refreshRemoveButtonsUIforQuetionTag(self):
        self.clearBtnTagsList()

        lst = self.getLatestTagsList()
        if len(lst) == 0:
            btn = QPushButton(u"Empty Tags", self)
            btn.setEnabled(False)
            self.btnTagsList.addWidget(btn)
            return

        for item in lst :
            strButtonTitle = u"x %s" % (item)
            btn=QPushButton(strButtonTitle, self)
            btn.strCurrTag = item
            btn.clicked.connect(lambda: self.onbtnRemoveTagClicked( btn.strCurrTag))
            self.btnTagsList.addWidget(btn)
            
    def onbtnRemoveTagClicked(self, strRemoveTag):
        strMessage = "[onbtnRemoveTagClicked] %s" %(strRemoveTag)
        print (strMessage)

        self.setLatestCurrentTagsDict(strRemoveTag, Qt.Unchecked)

    def getLatestCurrentTags(self):
        if self.dicNewTagsBuffer.has_key(self.nQIndex):
            return self.dicNewTagsBuffer[self.nQIndex]
        else:
            return self.latex.getQuestionTagList(self.nQIndex)


    def setLatestCurrentTagsDict(self, strTagName, nChecked):
        lst =self.getLatestCurrentTags()
        if nChecked == Qt.Unchecked:
            if strTagName in lst:
                lst.remove(strTagName)
        else:
            if strTagName not in lst:
                lst.append(strTagName)
        lstori = self.getLatestCurrentTags()
        if self.isTagsListDifferent(lst,lstori):
            self.dicNewTagsBuffer[self.nQIndex] = lst
        print ("[self.dicNewTagsBuffer]:" +str(self.dicNewTagsBuffer) )
        self.refreshTagsUI()


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
        pass

    def refreshTagsUI(self):
        self.refreshTagCheckedUIListData()
        self.refreshRemoveButtonsUIforQuetionTag()

    def refreshTagCheckedUIListData(self):
        lstTags = self.getLatestTagsList()
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
        self.setLatestCurrentTagsDict(sender.strTagName ,state)

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
        strMsg = u"Are you sure you want to exit the program? \n" \
                 u"(Yes\\Save and Yes\\No)"
        reply = QtGui.QMessageBox.question(self, u'Message',
                                           strMsg, QtGui.QMessageBox.Save, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Save:
            self.saveUpdatedTagIntoFile()
            event.accept()
        elif reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        pass

app=QApplication(sys.argv)
QuestionEditor=QuestionTagsEditor()

QuestionEditor.show()
sys.exit(app.exec_())