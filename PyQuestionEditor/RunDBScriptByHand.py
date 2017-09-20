#coding=utf-8

import timeit
from HDYLatexParserFromDB import HDYLatexParserFromDB


constQuestionsTableName = u"EXAM01"
constQuestionTagRealtionTableName = u"question_tag_relationship"
constTagTableName = u"questiontags"

constdefaultname = u"test.sqlitedb"


def add99BookTagIntoDB():
    """
    強迫新增這些 Tags Book 到DB檔案內
    :return:
    """
    dbLatex = HDYLatexParserFromDB(constdefaultname)
    dbLatex.read()
    n99ID = 130
    nGroupId = 2
    lstBook =[u'B1', u'B2', u'B3',u'B4',u'B5',u'B6']
    for tagstr in lstBook:
        strSQL = u'''INSERT INTO %s (TAG_STR, group_id, parent_id) VALUES ('%s', %d, %d)
                  ''' % (constTagTableName,tagstr,nGroupId,n99ID)
        dbLatex.executeSQL(strSQL)
    dbLatex.commitDB()

def add99RootTagIntoDB():
    """
    強迫新增 Tag Book 到DB檔案內
    :return:
    """
    dbLatex = HDYLatexParserFromDB(constdefaultname)
    dbLatex.read()
    strTag = u'99課綱'
    nGroupId= 1

    strSQL = u'''INSERT INTO %s (TAG_STR, group_id, parent_id) VALUES ('%s', %d, NULL)
              ''' % (constTagTableName, strTag, nGroupId)

    dbLatex.executeSQL(strSQL)
    dbLatex.commitDB()

def load99TreeIntoJason():
    dbLatex = HDYLatexParserFromDB(constdefaultname)
    rootID = 130
    dbLatex.read()
    strR = getNodeString(130, dbLatex)
    print(strR)

def getNodeString(nCurrentID, dbLatex, PARENT_TAG_STR = None):
    """
    由資料庫當中讀出 D3 tree diagram 可用的json node 結構
    :param nCurrentID: 由此ID 以下
    :param dbLatex: 可以使用的 Latex DB file object
    :param PARENT_TAG_STR: Parent node
    :return:
    """
    strR = u''
    strSQL = u'''SELECT tag_id, TAG_STR, parent_id, group_id from %s  WHERE tag_id = %d''' %(constTagTableName, nCurrentID)
    row = dbLatex.getRowBySQL(strSQL)
    name = row[1]
    nIdGroup = row[3]

    dictTagIDMapCount = dbLatex.getDictTagIDMapQuestionCount()

    if PARENT_TAG_STR == None:
        parent = u"null"
    else:
        parent = PARENT_TAG_STR

    strSQLs = u'''SELECT tag_id, TAG_STR, parent_id from %s  WHERE parent_id = %d order by TAG_SORTED_W''' % (constTagTableName, nCurrentID)
    rows = dbLatex.getRowsBySQL(strSQLs)
    lst = []

    for row in rows:
        lst.append(getNodeString( row[0],dbLatex, name) )

    lststr = ",".join(lst)
    if dictTagIDMapCount.has_key(nCurrentID):
        name = name + u"(%d)" % ( dictTagIDMapCount[nCurrentID],)

    webstring = u"/tagged/%d" % (nCurrentID, )

    if len(lst)==0:
        strR = u'{"name":"%s", "parent": "%s", "webpage": "%s"}' %(name,parent, webstring)
    else:
        childrenKey = "children"
        if nIdGroup == 3: #先不要展開
            childrenKey = "_children"
        strR = u'{"name":"%s", "parent": "%s", "webpage": "%s","%s":[%s]}' % (name, parent, webstring, childrenKey,lststr)

    return strR


def runMainFun():
    #run all pictures
    print("Runing....Please wait...")
    timer_start = timeit.default_timer()

    #add99RootTagIntoDB()
    #add99BookTagIntoDB()
    load99TreeIntoJason()
    timer_end = timeit.default_timer()
    print("This program Time usage:", timer_end - timer_start, " sec(s)")

if __name__ == '__main__':
    runMainFun()