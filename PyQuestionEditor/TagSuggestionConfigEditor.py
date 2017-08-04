
import sys, os, re, codecs
import difflib
from PyQt4.Qt import Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject, SIGNAL
import TagSuggestionConfigWidget
from TagSuggestionConfigWidget import Ui_TagSuggestionConfigEditor as TagSuggestionConfigWidget


constSuggestionTag = u"SuggestionTag.ini"

from PyQt4.QtGui import *

class MainWindow(QMainWindow, TagSuggestionConfigWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        #Load config
        import ConfigParser
        self.configSuggestionTag = ConfigParser.ConfigParser()
        self.configSuggestionTag.readfp(codecs.open(constSuggestionTag,u"r",u"utf8"))
        self.completerKeyWord = QCompleter(self.configSuggestionTag.sections()) #Keyword is the section of ini file.
        self.edtKeword.setCompleter(self.completerKeyWord)

    def onChangeKeyWord(self):
        strKeyWord = unicode(self.edtKeword.text())
        if strKeyWord in self.configSuggestionTag.sections():
            self.updateUIByKeyword(strKeyWord)
        else:
            print("[WARNING]There is no matched keyword.")
        pass

    def updateUIByKeyword(self, strKeyWord):
        import ast
        lst=ast.literal_eval(self.configSuggestionTag.get(strKeyWord, u'lst'))
        lstSectionInChap = ast.literal_eval(self.configSuggestionTag.get(strKeyWord, u'seclist'))

        self.lvSection.setModel(QStringListModel(lstSectionInChap))
        self.lvTag.setModel(QStringListModel(lst))

    def onSelectNewClick(self):
        print("[onSelectNewClick]")
        self.onChangeKeyWord()


    def onSectionAddRemoveClick(self):
        print("[onSectionAddRemoveClick]")


    def onTagAddRemoveClick(self):
        print("[onTagonTagAddRemoveClick]")
        pass

app = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
