# -*- coding: utf-8 -*-
import jieba
constDicMath = u"QDbML\\AllMathTerm_ByHand.txt"
constBigDict = u"QDbReport\\dict.txt.big"

class Jiebaer:
    def __init__(self):
        self.bInit = False

    def initialize(self):
        jieba.set_dictionary(constBigDict)
        jieba.load_userdict(constDicMath)

    def getJiebaCutList(self, strInput, bSkipSpace=False):
        if not self.bInit :
            #First Use: to load the dict/model
            self.initialize()
            self.bInit = True

        words = jieba.cut(strInput, cut_all=False)
        lstWords = []
        if bSkipSpace:
            for item in words:
                    if not item.isspace():
                        lstWords.append(item)
            return lstWords
        else:
            return words