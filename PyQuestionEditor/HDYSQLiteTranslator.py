#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        ? tex ??????? SQLite DB
# Purpose:
#
# Author:      user
#
# Created:     24/07/2017
# Copyright:   (c) user 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sqlite3
from HDYLatexParser import HDYLatexParser as texParser
from HDYLatexParserFromDB import HDYLatexParserFromDB as DBParser
from HDYQuestionParser import HDYQuestionParser as QParser

def createTagsTable():
    """
    開啟相關Tag的資料表
    :return:
    """
    conn = sqlite3.connect('test.sqlitedb')

    print "Opened database successfully";

    conn.execute(''' CREATE TABLE question_tag_relationship
                            (
                             relation_id INTEGER PRIMARY KEY AUTOINCREMENT ,
                             question_id INTEGER NOT NULL,
                             tag_id INTEGER NOT NULL
                             );
                    ''')
    conn.commit()

    conn.execute(''' CREATE TABLE questiontags
                            (
                             tag_id INTEGER PRIMARY KEY AUTOINCREMENT ,
                             TAG_STR TEXT UNIQUE NOT NULL
                             );
                    ''')
    conn.commit()

def createDBandTable():
    conn = sqlite3.connect('test.sqlitedb')

    print "Opened database successfully";

    conn.execute(''' CREATE TABLE EXAM01
                        (question_id INTEGER PRIMARY KEY AUTOINCREMENT ,
                         EXAMINFO_STR TEXT UNIQUE NOT NULL ,
                         EXAMINFO_YEAR INT NOT NULL,
                         EXAMINFO_EXAM_TYPE TEXT NOT NULL,
                         EXAMINFO_QUESTION_STYLE TEXT NOT NULL,
                         EXAMINFO_QUESTION_NUMBER TEXT NOT NULL,
                         EXAMANSRATEINFO_P INT NOT NULL,
                         EXAMANSRATEINFO_PH INT NOT NULL,
                         EXAMANSRATEINFO_PM INT NOT NULL,
                         EXAMANSRATEINFO_PL INT NOT NULL,
                         QBODY TEXT NOT NULL,
                         QFROMS TEXT NOT NULL,
                         QANS TEXT NOT NULL,
                         QSOLLIST TEXT NOT NULL,
                         QEMPTYSPACE TEXT NOT NULL
                         );

                ''')
    conn.commit()

def moveDataFromFiletoDB():
    lstFileNameList = []
    dbParser = DBParser('test.sqlitedb')
    for number in range(91, 107):
        strNumber = u"Exam01All\\q%03d.tex" % number
        lstFileNameList.append(strNumber)

    for strFileName in lstFileNameList:
        dbParser.appendTexFile(strFileName)

def movedataFromDBtoFile():
    dbParser = DBParser('test.sqlitedb')
    dbParser.saveSqliteDBIntoTexFileByYears()



def main():
    #PartI:
    createDBandTable()
    createTagsTable()
    moveDataFromFiletoDB()

    #PartII:
    #movedataFromDBtoFile()

    #PartIII: Try to load tag in exam01 and save it into table('question_tag_relationship')

if __name__ == '__main__':
    main()
