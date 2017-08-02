
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

    def onSelectNewClick(self):
        print("[onSelectNewClick]")

    def onSectionAddRemoveClick(self):
        print("[onSectionAddRemoveClick]")
        pass

    def onTagAddRemoveClick(self):
        print("[onTagonTagAddRemoveClick]")
        pass

app = QtGui.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
