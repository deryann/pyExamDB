# -*- coding: utf-8 -*-
import jieba
constDicMath = u"QDbML\\AllMathTerm_ByHand.txt"
constBigDict = u"QDbReport\\dict.txt.big"
jieba.set_dictionary(constBigDict)
jieba.load_userdict(constDicMath)

def getJiebaCutList(strInput, bSkipSpace=False):
    words = jieba.cut(strInput, cut_all=False)
    lstWords = []
    if bSkipSpace:
        for item in words:
                if not item.isspace():
                    lstWords.append(item)
        return lstWords
    else:
        return words

