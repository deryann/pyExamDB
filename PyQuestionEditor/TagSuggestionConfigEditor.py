# -*- coding: utf-8 -*-
import sys, os, re, codecs
from backports import configparser
import configparser
import ast
import difflib
from PyQt4.Qt import Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, SIGNAL
import TagSuggestionConfigWidget
from TagSuggestionConfigWidget import Ui_TagSuggestionConfigEditor as TagSuggestionConfigWidget

constSuggestionTag = u"SuggestionTag.ini"

from PyQt4.QtGui import *

def stringListToUnicodeString(lstInput):
    strR = u"["
    nTotal = len(lstInput)
    for k in range(nTotal):
        strR = strR + "u\"" + lstInput[k] + "\""
        if k < nTotal - 1:
            strR = strR + u","
    strR = strR + u"]"
    return strR


class HDYStringListModel(QStringListModel):
    def __init__(self , *var_args_tuple):
        QStringListModel.__init__(self, *var_args_tuple)

    def getStringList(self):
        qstrlst = self.stringList()
        lstReturn = [ unicode(item.toUtf8() , encoding="UTF-8" ) for item in qstrlst]
        return lstReturn

    def getUnicodeStringForStringList(self):
        """
        將此List 變成一個合適的中括弧括起來的字串
        :return: stR
        """
        lst = self.getStringList()
        return stringListToUnicodeString(lst)

    def getUnicodeStringForStringListWithAppended(self, strAppended):
        lst = self.getStringList()
        lst.append(strAppended)
        return stringListToUnicodeString(lst)

    def getUnicodeStringForStringListWithRemoving(self, strRemoving):
        lst =self.getStringList()
        lst.remove(strRemoving)
        return stringListToUnicodeString(lst)

class MainWindow(QMainWindow, TagSuggestionConfigWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.strKeyWord=u''

        #Load config
        self.configSuggestionTag = configparser.ConfigParser()
        self.configSuggestionTag.read(constSuggestionTag, encoding='utf-8')

        self.modelKeyword = HDYStringListModel(self.configSuggestionTag.sections())
        self.cbKeyword.setModel(self.modelKeyword)

    def onCbKeywordChang(self,qstr):
        if self.strKeyWord !='':
            self.onSaveLvSectionModel()
        self.strKeyWord = unicode(self.cbKeyword.currentText())
        if self.strKeyWord in self.configSuggestionTag.sections():
            self.updateUIByKeyword()

    def onLvSectionPressed(self, qindex):
        print ("[onLvSectionPressed]")
        print(qindex)
        pass

    def onLvTagPressed(self,qindex):
        print ("[onLvTagPressed]")
        print(qindex)
        pass

    def updateUIByKeyword(self):
        lst=ast.literal_eval(self.configSuggestionTag.get(self.strKeyWord, u'lst'))
        lstSectionInChap = ast.literal_eval(self.configSuggestionTag.get(self.strKeyWord, u'seclist'))
        self.strlstModelSectionInChap = HDYStringListModel(lstSectionInChap)
        self.lvSection.setModel(self.strlstModelSectionInChap)
        self.strlstModelTag = HDYStringListModel(lst)
        self.lvTag.setModel(self.strlstModelTag)

    def onSelectNewClick(self):
        print("[onSelectNewClick]")
        self.onChangeKeyWord()

    def backupINIFile(self):
        from time import gmtime, strftime
        strBachUpFileName = constSuggestionTag+strftime("%Y%m%d%H%M%S", gmtime())+".bak"
        import shutil
        shutil.copyfile(constSuggestionTag,strBachUpFileName)

    def onSectionAddRemoveClick(self):
        print("[onSectionAddRemoveClick]")
        strBuffer = unicode(self.edtSection.text())
        if strBuffer == u"":
            #Save List view
            strword = self.strlstModelSectionInChap.getUnicodeStringForStringList()
        elif strBuffer in self.strlstModelSectionInChap.getStringList():
            #remove
            strword = self.strlstModelSectionInChap.getUnicodeStringForStringListWithRemoving(strBuffer)
        else:
            #add
            strword = self.strlstModelSectionInChap.getUnicodeStringForStringListWithAppended(strBuffer)

        self.configSuggestionTag.set(self.strKeyWord, u'seclist', strword)
        self.backupINIandSave()
        self.updateUIByKeyword()

    def onSaveLvSectionModel(self):
        strword = self.strlstModelSectionInChap.getUnicodeStringForStringList()
        bNeedtoUpdateIntoFile = (strword != self.configSuggestionTag.get(self.strKeyWord, u'seclist'))
        if bNeedtoUpdateIntoFile:
            self.configSuggestionTag.set(self.strKeyWord, u'seclist', strword)
            self.backupINIandSave()
            self.updateUIByKeyword()
        else:
            print(u"[un-necessary to updated to file]")

    def backupINIandSave(self):
        print(u'backupINIandSave')
        self.backupINIFile()
        f = codecs.open(constSuggestionTag, 'w', 'utf-8')
        self.configSuggestionTag.write(f)
        f.close()

    def onTagAddRemoveClick(self):
        print("[onTagonTagAddRemoveClick]")
        pass

    def msgbtn(self,i):
        print ("Button pressed is:"+ i.text())

    def showWarningDialog(self,strWarningKeyWord):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(strWarningKeyWord)
        #msg.setInformativeText(strWarningKeyWord)
        msg.setWindowTitle("Warning Message")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.buttonClicked.connect(self.msgbtn)
        retval = msg.exec_()
        print ("value of pressed message box button:", retval)
        pass

app = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
