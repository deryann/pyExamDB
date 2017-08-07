# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TagSuggestionConfig.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_TagSuggestionConfigEditor(object):
    def setupUi(self, TagSuggestionConfigEditor):
        TagSuggestionConfigEditor.setObjectName(_fromUtf8("TagSuggestionConfigEditor"))
        TagSuggestionConfigEditor.resize(867, 584)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Consolas"))
        font.setPointSize(12)
        TagSuggestionConfigEditor.setFont(font)
        self.centralwidget = QtGui.QWidget(TagSuggestionConfigEditor)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gbKeyWord = QtGui.QGroupBox(self.centralwidget)
        self.gbKeyWord.setMinimumSize(QtCore.QSize(0, 80))
        self.gbKeyWord.setMaximumSize(QtCore.QSize(16777215, 80))
        self.gbKeyWord.setObjectName(_fromUtf8("gbKeyWord"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.gbKeyWord)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cbKeyword = QtGui.QComboBox(self.gbKeyWord)
        self.cbKeyword.setObjectName(_fromUtf8("cbKeyword"))
        self.horizontalLayout.addWidget(self.cbKeyword)
        self.btnSelectNew = QtGui.QPushButton(self.gbKeyWord)
        self.btnSelectNew.setObjectName(_fromUtf8("btnSelectNew"))
        self.horizontalLayout.addWidget(self.btnSelectNew)
        self.btnMore = QtGui.QPushButton(self.gbKeyWord)
        self.btnMore.setObjectName(_fromUtf8("btnMore"))
        self.horizontalLayout.addWidget(self.btnMore)
        self.verticalLayout_2.addWidget(self.gbKeyWord)
        self.gbSection = QtGui.QGroupBox(self.centralwidget)
        self.gbSection.setObjectName(_fromUtf8("gbSection"))
        self.verticalLayout = QtGui.QVBoxLayout(self.gbSection)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widgetEditSection = QtGui.QWidget(self.gbSection)
        self.widgetEditSection.setObjectName(_fromUtf8("widgetEditSection"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widgetEditSection)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.edtSection = QtGui.QLineEdit(self.widgetEditSection)
        self.edtSection.setObjectName(_fromUtf8("edtSection"))
        self.horizontalLayout_2.addWidget(self.edtSection)
        self.btnSectionAddRemove = QtGui.QPushButton(self.widgetEditSection)
        self.btnSectionAddRemove.setObjectName(_fromUtf8("btnSectionAddRemove"))
        self.horizontalLayout_2.addWidget(self.btnSectionAddRemove)
        self.verticalLayout.addWidget(self.widgetEditSection)
        self.lvSection = QtGui.QListView(self.gbSection)
        self.lvSection.setObjectName(_fromUtf8("lvSection"))
        self.verticalLayout.addWidget(self.lvSection)
        self.verticalLayout_2.addWidget(self.gbSection)
        self.gbTagItems = QtGui.QGroupBox(self.centralwidget)
        self.gbTagItems.setObjectName(_fromUtf8("gbTagItems"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.gbTagItems)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.widget_2 = QtGui.QWidget(self.gbTagItems)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.edtTag = QtGui.QLineEdit(self.widget_2)
        self.edtTag.setObjectName(_fromUtf8("edtTag"))
        self.horizontalLayout_3.addWidget(self.edtTag)
        self.btnTagAddremove = QtGui.QPushButton(self.widget_2)
        self.btnTagAddremove.setObjectName(_fromUtf8("btnTagAddremove"))
        self.horizontalLayout_3.addWidget(self.btnTagAddremove)
        self.verticalLayout_3.addWidget(self.widget_2)
        self.lvTag = QtGui.QListView(self.gbTagItems)
        self.lvTag.setObjectName(_fromUtf8("lvTag"))
        self.verticalLayout_3.addWidget(self.lvTag)
        self.verticalLayout_2.addWidget(self.gbTagItems)
        TagSuggestionConfigEditor.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(TagSuggestionConfigEditor)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 867, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        TagSuggestionConfigEditor.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(TagSuggestionConfigEditor)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        TagSuggestionConfigEditor.setStatusBar(self.statusbar)

        self.retranslateUi(TagSuggestionConfigEditor)
        QtCore.QObject.connect(self.btnSelectNew, QtCore.SIGNAL(_fromUtf8("clicked()")), TagSuggestionConfigEditor.onSelectNewClick)
        QtCore.QObject.connect(self.btnSectionAddRemove, QtCore.SIGNAL(_fromUtf8("clicked()")), TagSuggestionConfigEditor.onSectionAddRemoveClick)
        QtCore.QObject.connect(self.btnTagAddremove, QtCore.SIGNAL(_fromUtf8("clicked()")), TagSuggestionConfigEditor.onTagAddRemoveClick)
        QtCore.QObject.connect(self.edtSection, QtCore.SIGNAL(_fromUtf8("returnPressed()")), TagSuggestionConfigEditor.onSectionAddRemoveClick)
        QtCore.QObject.connect(self.edtTag, QtCore.SIGNAL(_fromUtf8("returnPressed()")), TagSuggestionConfigEditor.onTagAddRemoveClick)
        QtCore.QObject.connect(self.cbKeyword, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), TagSuggestionConfigEditor.onCbKeywordChang)
        QtCore.QObject.connect(self.lvSection, QtCore.SIGNAL(_fromUtf8("pressed(QModelIndex)")), TagSuggestionConfigEditor.onLvSectionPressed)
        QtCore.QObject.connect(self.lvTag, QtCore.SIGNAL(_fromUtf8("pressed(QModelIndex)")), TagSuggestionConfigEditor.onLvTagPressed)
        QtCore.QMetaObject.connectSlotsByName(TagSuggestionConfigEditor)

    def retranslateUi(self, TagSuggestionConfigEditor):
        TagSuggestionConfigEditor.setWindowTitle(_translate("TagSuggestionConfigEditor", "Tag suggestion config Editor", None))
        self.gbKeyWord.setTitle(_translate("TagSuggestionConfigEditor", "Key Word", None))
        self.btnSelectNew.setText(_translate("TagSuggestionConfigEditor", "Select/New", None))
        self.btnMore.setText(_translate("TagSuggestionConfigEditor", "...", None))
        self.gbSection.setTitle(_translate("TagSuggestionConfigEditor", "Section List", None))
        self.btnSectionAddRemove.setText(_translate("TagSuggestionConfigEditor", "Add/Remove", None))
        self.gbTagItems.setTitle(_translate("TagSuggestionConfigEditor", "Tag Item List", None))
        self.btnTagAddremove.setText(_translate("TagSuggestionConfigEditor", "Add/Remove", None))

