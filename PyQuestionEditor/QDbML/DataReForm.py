# -*- coding: utf-8 -*-

import pandas as pd
import os
import codecs

#Use 高中以下數學名詞資料庫 from 國家教研究研究院
constNameFileName = u"Term_235_0_utf8.csv"
constNameFileNameHDY = u"HDYCompareNaming.txt"
constAllMathTermFile = u"AllMathTerm.txt"

def isSingleTerm(strMathTerm):
    if strMathTerm.find(u"[")==-1:
        return True
    else:
        return False

def unzipTerm(strInput):
    """
    將有[] 的原型給取出
    :return:
    """
    #TODO: 如何解決複合型的 [][]
    lstR = []
    import re
    strA = re.sub('[\\[\\]]', '', strInput)
    strB = re.sub('\[[^\]]\]', '', strInput)
    lstR.append(strA.strip())
    lstR.append(strB.strip())
    return lstR

def translateAsMathTerm(oriName):
    '''
    將字元切割，或者是生成(含[]與不含[])
    :param oriName: 輸入的字
    :return:
    '''
    lstR = []
    lst = oriName.split(u"；")
    for item in lst:
        if isSingleTerm(item):
            lstR.append(item)
        else:
            lstForSameTerm = unzipTerm(item)
            lstR.extend(lstForSameTerm)
    return lstR


def main():

    strFileName = constNameFileName
    lstUsecols = [u"系統編號",u"英文名稱",u"中文名稱",u"圖片",u"備註",u"更新時間"]
    nameData = pd.read_csv(strFileName, encoding='utf8', usecols=lstUsecols)
    print (nameData)
    setMathTerm = set()
    with codecs.open(constNameFileNameHDY, "w", "utf-8") as fpt:
        for index in range(len(nameData.index)):
            row = nameData.iloc[index]
            oriName = row[u"中文名稱"]
            lstHDYMathTerm = translateAsMathTerm (oriName)
            fpt.write(oriName)
            fpt.write(u" ")
            fpt.write( ', '.join(lstHDYMathTerm))
            fpt.write(os.linesep)
            setMathTerm=setMathTerm.union( set(lstHDYMathTerm))

    with codecs.open(constAllMathTermFile, "w", "utf-8") as fptMath:
        lstSored = sorted(setMathTerm)
        for mathTerm in lstSored:
            fptMath.write(mathTerm+os.linesep)

if __name__ == '__main__':
    main()