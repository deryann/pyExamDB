
# -*- coding: utf-8 -*-
import sys, os, re, codecs
from backports import configparser
import configparser
import difflib
from PyQt4.Qt import Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, SIGNAL
import TagSuggestionConfigWidget
from TagSuggestionConfigWidget import Ui_TagSuggestionConfigEditor as TagSuggestionConfigWidget


constSuggestionTag = u"SuggestionTag.ini"

from PyQt4.QtGui import *

class HDYStringListModel(QStringListModel):
    def __init__(self , *var_args_tuple):
        QStringListModel.__init__(self, *var_args_tuple)

    def getStringList(self):
        qstrlst = self.stringList()
        lstReturn = [ unicode(item) for item in qstrlst]
        return lstReturn



class MainWindow(QMainWindow, TagSuggestionConfigWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        #Load config

        self.configSuggestionTag = configparser.ConfigParser()
        self.configSuggestionTag.read(constSuggestionTag, encoding='utf-8')
        self.completerKeyWord = QCompleter(self.configSuggestionTag.sections()) #Keyword is the section of ini file.
        self.edtKeword.setCompleter(self.completerKeyWord)

    def onChangeKeyWord(self):
        self.strKeyWord = unicode(self.edtKeword.text())

        if self.strKeyWord in self.configSuggestionTag.sections():
            self.updateUIByKeyword(self.strKeyWord)
        else:
            print("[WARNING]There is no matched keyword.")
        pass

    def updateUIByKeyword(self, strKeyWord):
        import ast
        lst=ast.literal_eval(self.configSuggestionTag.get(strKeyWord, u'lst'))
        lstSectionInChap = ast.literal_eval(self.configSuggestionTag.get(strKeyWord, u'seclist'))
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
        self.backupINIFile()
        lst = self.strlstModelSectionInChap.getStringList()
        strword =  str(lst)
        self.configSuggestionTag.set(self.strKeyWord, u'seclist', unicode(lst))
        # 現在存入的字串很怪 沒有存入中文字的格式, 存入了\uxxxx的格式
        self.configSuggestionTag.write(codecs.open(constSuggestionTag, 'w', 'utf-8'))

    def onTagAddRemoveClick(self):
        print("[onTagonTagAddRemoveClick]")
        pass

app = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
