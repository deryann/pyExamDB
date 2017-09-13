# -*- coding: utf-8 -*-
import codecs

constFileName = u"QDbML\\AllMathTerm_ByHand.txt"
def getMathTermList():
    lst = []
    with codecs.open(constFileName, "r", "utf-8") as fptdata:
        lst = fptdata.read().splitlines()
    return lst