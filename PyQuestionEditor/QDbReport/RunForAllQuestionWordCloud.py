#coding=utf-8
import operator
import os
import codecs
import re
from HDYQuestionParser import HDYQuestionParser, getListOfTagFromString


import jieba.analyse
from os import path
from scipy.misc import imread
import matplotlib as mpl
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from HDYQuestionParserFromDB import HDYQuestionParserFromDB
from HDYLatexParser import HDYLatexParser
from HDYLatexParserFromDB import HDYLatexParserFromDB
from TexToPNG.PNGMaker import PNGMaker

import sqlite3
constQuestionsTableName = u"EXAM01"
constQuestionTagRealtionTableName = u"question_tag_relationship"
constTagTableName = u"questiontags"

constdefaultname = u"test.sqlitedb"
constLogFile = u"JiebaHDY.log"
constAllQBODY = u'allqbody.txt'
constAllQBODYAfterPreProcess = u'allqbodyAfterPP.txt'
constCutResultFileName = u'CutResult.txt'
constCutResultFileName2 = u'CutResultWithMathTerm.txt'

constDicMath = u"..\\QDbML\\AllMathTerm_ByHand.txt"
strTikzTemplate = u"""\\begin{tikzpicture}%s
\\end{tikzpicture}

"""
import random

def hdy_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    #return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)
    return "rgb(%d, %d, %d)" % (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))

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

def doJieba(strfilename, content):
    with codecs.open(strfilename, "w", "utf-8") as fptcutfile:
        words = jieba.cut(content, cut_all=False)
        lstWords = []
        for item in words:
            if not item.isspace():
                lstWords.append(item)
        fptcutfile.write(os.linesep.join(lstWords))

        #d = {x: lstWords.count(x) for x in lstWords}
        #print(d)

        #sorted_d = sorted(d.items(), key=operator.itemgetter(1))
        #for item in sorted_d:
        #    fptcutfile.write(u"word: %s count %d %s" % (unicode(item[0]), item[1], os.linesep,))


def mainReport():
    with codecs.open(constLogFile,"w", "utf-8") as fpt:
        if not os.path.isfile(constAllQBODY):
            with codecs.open(constAllQBODY,"w", "utf-8") as fptdata:
                dbLatex = HDYLatexParserFromDB(constdefaultname)
                dbLatex.read()
                nCount = dbLatex.nCountQ
                for i in range(nCount):
                    qPt = dbLatex.getQuestionObject(i)

                    strQBODY =qPt.getQBODY()
                    fptdata.write(strQBODY+os.linesep)
                    strlog = (u"NO %d QBODY done !" + os.linesep) % (i, )
                    fpt.write(strlog)

        lstReplaceToEmpty = [u"\\begin{QOPS}", u"\\end{QOPS}", u"\\QOP",
                             ]
        #Preprocess AllBodyData
        with codecs.open(constAllQBODY,"r", "utf-8") as fptdata:
            if not os.path.isfile(constAllQBODYAfterPreProcess):
                content = fptdata.read()

                #skip all math mode
                content = skipAllMathMode(content)

                lst = re.findall(u"\\\\begin{tikzpicture}(.*?)\\\\end{tikzpicture}", content, re.DOTALL)

                for item in lstReplaceToEmpty:
                    content = content.replace(item, u'')

                for item in lst:
                    stritem = u"\\begin{tikzpicture}"+item+u"\\end{tikzpicture}"
                    content = content.replace(stritem, u'')


                with codecs.open(constAllQBODYAfterPreProcess, "w", "utf-8") as fptout:
                    fptout.write(content)

        #Load Data to Word cloud.
        with codecs.open(constAllQBODYAfterPreProcess, "r", "utf-8") as fptdata:
            mpl.rcParams['font.sans-serif'] = ['FangSong']
            jieba.set_dictionary('dict.txt.big')
            content = fptdata.read()
            #Type I
            doJieba(constCutResultFileName, content)
            jieba.load_userdict(constDicMath)

            # Type II()Better
            doJieba(constCutResultFileName2, content)

            # tags extraction based on TF-IDF algorithm
            tags = jieba.analyse.extract_tags(content, topK=100, withWeight=False)
            text = os.linesep.join(tags)
            text = unicode(text)
            fpt.write(text)

    #read the mask
    d = path.dirname(__file__)
    mask_coloring = imread(path.join(d, "mask01.png"))

    wc = WordCloud(font_path=path.join(d,'fonts\msjh.ttc'),
                   background_color="black", max_words=50, mask=None,
                   max_font_size=90, random_state=42,width=400,height=400)

    # generate word cloud
    wc.generate(text)

    # generate color from image
    image_colors = ImageColorGenerator(mask_coloring)


    #plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    plt.imshow(wc.recolor(color_func=hdy_color_func))
    plt.axis("off")
    plt.show()
    pass

if __name__ == '__main__':
    mainReport()