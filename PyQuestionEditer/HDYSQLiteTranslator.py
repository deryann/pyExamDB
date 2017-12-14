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

def createDBandTable():
    import sqlite3

    conn = sqlite3.connect('test.sqlitedb')

    print "Opened database successfully";

    conn.execute(''' CREATE TABLE EXAM01
                        (EXAMINFO_STR TEXT PRIMARY KEY NOT NULL ,
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
                         QTAGS TEXT NOT NULL,
                         QANS TEXT NOT NULL,
                         QSOLLIST TEXT NOT NULL,
                         QEMPTYSPACE TEXT NOT NULL,
                         FULLQUESTION TEXT NOT NULL
                         );

                ''')
    conn.commit()

def moveDataFromFiletoDB():
    import sqlite3

    conn = sqlite3.connect('test.sqlitedb')

    from HDYLatexParser import HDYLatexParser as texParser
    from HDYQuestionParser import HDYQuestionParser as QParser

    lstFileNameList = []
    #for number in range(91,107):
    for number in range(91,107):
        strNumber = u"Exam01All\\q%03d.tex" % number
        lstFileNameList.append(strNumber)

    for strFileName in lstFileNameList:
        fPt = texParser(strFileName)
        fPt.read()
        fPt.getReport()
        for nIndex in range(fPt.getCountOfQ()):

            Qpt = QParser(fPt.getQuestion(nIndex))
            print(Qpt.getExamInfoString())
            strSQL = "INSERT INTO EXAM01 %s" % Qpt.getSQLString()
            print("==========================================")
            print(strSQL)
            print("==========================================")
            conn.execute(strSQL)
            conn.commit()

    print "Records created successfully";
    pass

def main():
    createDBandTable()
    moveDataFromFiletoDB()

if __name__ == '__main__':
    main()
