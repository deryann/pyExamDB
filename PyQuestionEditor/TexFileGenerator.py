#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        TexFileGenerator
# Purpose:
#
# Author:      user
#
# Created:     12/07/2017
# Copyright:   (c) user 2017
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


##
# 程式所使用的常數區
#
#
const99TagFileName = u"99TagGroup.txt"
constAllStrTagFileName = u"allTags.txt"

constExamStringList = [u"學測",u"指考甲",u"指考乙"]
constExamYearStringList = [u"106",u"105"]
constExamQuestionStyleStringList = [u"單選",u"多選",u"選填",u"填充",u"計算"]


def generateTexFileTemplate():
    """
    利用無引數的物件，按照指定的題數做出空白的檔案來
    """
    strYear="105"
    strExam="學測"
    lstQstyle = [["單選","1","6"],["多選","7","13"],["選填","A","G"] ]
    strOutFileName = "105.tex"
    latexPt = HDYLatexParser(None)
    latexPt.newTemplate(strYear, strExam, lstQstyle, "105.tex")

def generateTexFileTemplateByCSVFile():
    """
    另用已經有的 csv 資料寫出Tex file
    """
    import pandas as pd
    strFileName= u"E:\\NCTUG2\\Code\\pyExamDBF5\\PyQuestionEditor\\exam_xc.csv"
    lstUsecols = [u'類別',u'年份',u'題型',u'題號',u'答案',u'章節', u'章節（短）',
        u'P',u'Ph',u'Pm',u'Pl',u'P90',u'P70',u'P50',u'P30',u'P10',u'T',u'D',u'D1',u'D2',u'D3',u'D4',
        u'TA',u'TB',u'TC',u'TD',u'TE',u'HA',u'HB',u'HC',u'HD',u'HE',u'LA',u'LB',u'LC',u'LD',u'LE']
    exam = pd.read_csv(strFileName, encoding = 'utf8',usecols = lstUsecols)

    print(exam[exam[u'年份']==106])
    latexPt = HDYLatexParser(None)
    latexPt.newTemplateByCsvInput(exam)

def generate83to90():

    dicTable = {
        83: [[u"單選", u"1", u"7"] ,[u"多選",u"8", u"10"],[u"選填",u"11", u"20"]],
        84: [[u"單選", u"1", u"7"] ,[u"多選",u"8", u"11"],[u"選填",u"12", u"20"]],
        85: [[u"單選", u"1", u"8"] ,[u"多選",u"9", u"14"],[u"選填",u"15", u"20"]],
        86: [[u"單選", u"1", u"8"] ,[u"多選",u"9", u"12"],[u"選填",u"13", u"20"]],
        87: [[u"單選", u"1", u"4"] ,[u"多選",u"5", u"10"],[u"選填",u"11", u"20"]],
        88: [[u"單選", u"1", u"3"] ,[u"多選",u"4", u"10"],[u"選填",u"11", u"20"]],
        89: [[u"單選", u"1", u"7"] ,[u"多選",u"8", u"10"],[u"選填",u"11", u"20"]],
        90: [[u"單選", u"1", u"3"] ,[u"多選",u"4", u"10"],[u"選填",u"11", u"20"]]}

    for nYear in dicTable.keys():
        strYear = unicode(nYear)
        strExam = u"學測"
        strOutputFileName = u"q%03d.tex" %(nYear,)
        lstQstyle = dicTable[nYear]
        latexPt = HDYLatexParser(None)
        latexPt.newTemplate(strYear, strExam, lstQstyle, strOutputFileName)
        pass
    pass

def main():
    #generateTexFileTemplateByCSVFile()
    generate83to90()
    pass

if __name__ == '__main__':
    main()
