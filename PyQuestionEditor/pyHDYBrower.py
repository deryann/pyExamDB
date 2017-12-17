#coding=utf-8
# -*- coding: utf-8 -*-
import os, sys

from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtGui import QGridLayout, QLineEdit, QWidget, QHeaderView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

def getChromeDriverPath():
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = BASE_DIR+os.sep +'..'+os.sep +'bin'+os.sep+'chromedriver.exe'
    return path

def getCurrentPath():
    return os.path.dirname(os.path.abspath(__file__))

class UrlInput(QLineEdit):
    def __init__(self, browser):
        super(UrlInput, self).__init__()
        self.browser = browser
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        url = QUrl(self.text())
        self.browser.load(url)


class JavaScriptEvaluator(QLineEdit):
    def __init__(self, page):
        super(JavaScriptEvaluator, self).__init__()
        self.page = page
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        frame = self.page.currentFrame()
        result = frame.evaluateJavaScript(self.text())

class ActionInputBox(QLineEdit):
    def __init__(self, page):
        super(ActionInputBox, self).__init__()
        self.page = page
        self.returnPressed.connect(self._return_pressed)

    def _return_pressed(self):
        frame = self.page.currentFrame()
        action_string = str(self.text()).lower()
        if action_string == "b":
            self.page.triggerAction(QWebPage.Back)
        elif action_string == "f":
            self.page.triggerAction(QWebPage.Forward)
        elif action_string == "s":
            self.page.triggerAction(QWebPage.Stop)
        elif action_string == "r":
            self.page.triggerAction(QWebPage.Reload)


class RequestsTable(QTableWidget):
    header = ["url", "status", "content-type"]

    def __init__(self):
        super(RequestsTable, self).__init__()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(self.header)
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setResizeMode(QHeaderView.ResizeToContents)

    def update(self, data):
        last_row = self.rowCount()
        next_row = last_row + 1
        self.setRowCount(next_row)
        for col, dat in enumerate(data, 0):
            if not dat:
                continue
            self.setItem(last_row, col, QTableWidgetItem(dat))

class Manager(QNetworkAccessManager):
    def __init__(self, table):
        QNetworkAccessManager.__init__(self)
        self.finished.connect(self._finished)
        self.table = table

    def _finished(self, reply):
        headers = reply.rawHeaderPairs()
        headers = {str(k):str(v) for k,v in headers}
        content_type = headers.get("Content-Type")
        url = reply.url().toString()
        status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        status, ok = status.toInt()
        self.table.update([url, str(status), content_type])


def runBrowser():
    app = QApplication(sys.argv)

    grid = QGridLayout()
    browser = QWebView()
    url_input = UrlInput(browser)
    requests_table = RequestsTable()

    manager = Manager(requests_table)
    page = QWebPage()
    page.setNetworkAccessManager(manager)
    browser.setPage(page)

    js_eval = JavaScriptEvaluator(page)
    action_box = ActionInputBox(page)

    grid.addWidget(url_input, 1, 0)
    grid.addWidget(action_box, 2, 0)
    grid.addWidget(browser, 3, 0)
    grid.addWidget(requests_table, 4, 0)
    grid.addWidget(js_eval, 5, 0)

    main_frame = QWidget()
    main_frame.setLayout(grid)
    main_frame.show()

    sys.exit(app.exec_())

def runWebBrower2():
    import webbrowser
    new = 2 # open in a new tab, if possible

    # open a public URL, in this case, the webbrowser docs
    url = "http://docs.python.org/library/webbrowser.html"
    url2 = "http://www.google.com"
    a=webbrowser.get()
    a.open(url, autoraise=False)
    import time
    time.sleep(10)
    a.open(url2)

def runWebBrower3():
    import time
    from selenium import webdriver

    driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
    driver.get('http://www.google.com/xhtml');
    time.sleep(5)  # Let the user actually see something!
    search_box = driver.find_element_by_name('q')
    search_box.send_keys('ChromeDriver')
    search_box.submit()
    time.sleep(5)  # Let the user actually see something!
    driver.quit()
    pass

def runWebBrower4():
    import time
    from selenium import webdriver
    driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
    driver.get('http://www.google.com/xhtml')
    time.sleep(5)  # Let the user actually see something!
    driver.get('http://udn.com')
    time.sleep(15)  # Let the user actually see something!
    driver.quit()
    pass


if __name__ == '__main__':
    runWebBrower4()