# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.Qt import *
from PyQt4.QtCore import pyqtSignal, QSize, Qt
import logging


class HDYNavigator(QWidget):

    indexChanged = pyqtSignal(int)

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.currentIndex = None
        self.nMax = 0
        self.setFixedWidth(200)
        self.prepareIndexSettingLayout()

    def reset(self):
        self.currentIndex = None

    def refresh(self):
        logging.debug ("[HDYNavigator][refresh]")
        # 事實上，秀出來的Index 是由 1 開始的
        self.edtIndex.setText(str(self.currentIndex + 1))

    def getIndex(self):
        return self.currentIndex

    def prepareIndexSettingLayout(self):
        """
        實作控制 index 決定按鈕驅動事件
        """
        self.setLayout(QHBoxLayout())
        self.layoutBtnsControlIndex = self.layout()

        self.btnFirst=QPushButton("|<", self)
        self.btnPrev=QPushButton("<",self)
        self.edtIndex = QLineEdit ("1", self)
        self.lblgap = QLabel(u"/",self)
        self.lblCount =  QLabel("0", self)
        self.btnNext=QPushButton(">",self)
        self.btnLast=QPushButton(">|",self)

        self.layoutBtnsControlIndex.addWidget(self.btnFirst)
        self.layoutBtnsControlIndex.addWidget(self.btnPrev)
        self.layoutBtnsControlIndex.addWidget(self.edtIndex)
        self.layoutBtnsControlIndex.addWidget(self.lblgap)
        self.layoutBtnsControlIndex.addWidget(self.lblCount)
        self.layoutBtnsControlIndex.addWidget(self.btnNext)
        self.layoutBtnsControlIndex.addWidget(self.btnLast)

        self.btnFirst.clicked.connect(self.onbtnFirstClicked)
        self.btnLast.clicked.connect(self.onbtnLastClicked)
        self.btnNext.clicked.connect(self.onbtnNextClicked)
        self.btnPrev.clicked.connect(self.onbtnPrevClicked)
        self.edtIndex.textChanged.connect(self.onedtIndexChaned)

    def onbtnFirstClicked(self):
        self.setCurrentIndex(0)

    def onbtnLastClicked(self):
        self.setCurrentIndex(self.nMax - 1)

    def onbtnNextClicked(self):
        self.setCurrentIndex(self.currentIndex + 1)

    def onbtnPrevClicked(self):
        self.setCurrentIndex(self.currentIndex - 1)

    def setMax(self, nInput):
        self.nMax = nInput
        self.lblCount.setText(unicode(self.nMax))

    def onedtIndexChaned(self, strText):
        try:
            nIndex= int (strText) -1
        except:
            nIndex=self.nQIndex
            pass
        self.setCurrentIndex(nIndex)

        logging.debug("onedtIndexChaned")
        pass

    def setCurrentIndex(self, nIndex):
        if nIndex < self.nMax and nIndex >= 0:
            nOricurrentIndex = self.currentIndex
            self.currentIndex = nIndex
            if nOricurrentIndex != nIndex:
                self.indexChanged.emit(nIndex)

            self.refresh()
