# -*- coding: utf-8 -*-
def skipAllMathMode(strInput):
    lst = strInput.split(u'$')
    nSplit =len(lst)
    strR = u''
    #TODO: Handle /$ case

    for i in range(nSplit):
        if (i%2)==0:
            #It is in text mode
            strR +=(u' ' + lst[i])
            pass
        elif (i%2)==1:
            #It is in math mode
            #strR += (u"$" + lst[i]+ u"$")
            pass

    return strR

