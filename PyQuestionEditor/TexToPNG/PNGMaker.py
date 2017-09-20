#coding=utf-8
import os, timeit,sys
import codecs
import hashlib
from PIL import Image as PILImage
from PIL import PngImagePlugin

constTempWorkFileMainWord = u"TempToPNG"
constTempWorkFileMainWordC = u'"TempToPNG"'
constTempWorkTexFile = constTempWorkFileMainWord+u".tex"
constWorkPath = u"E:\\NCTUG2\\Code\\pyExamDBDevUI\\PyQuestionEditor"

constTempWorkTexTemplate = u"""
% !TEX encoding = UTF-8 Unicode
% !TEX TS-program = xelatex
\\documentclass[12pt]{article}
\\usepackage{tikz}
\\usepackage{pgfplots}
\\usetikzlibrary{calc, arrows, patterns,angles ,positioning,quotes}
\\usetikzlibrary{decorations.markings}
\\usetikzlibrary{arrows.meta}

\\usepackage{tkz-euclide}
%==== Chinese Setting  ====== 

\\input{E:/NCTUG2/TEX/LatexCodeTemplate/inputFile/NONXeHeader.tex}
\\begin{document}
    \\begin{TeXtoEPS}
        %{{TikzStatment}}
    \\end{TeXtoEPS}
\\end{document}

"""

strTestContent = u"""\\begin{tikzpicture}[every edge quotes/.append style={auto, text=blue},
			x={(-0.25cm,-0.15cm)},
			y={(0.5cm,0cm)},
			z={(0cm,0.5cm)}]
			%%空間坐標中的CUBE 是以平面上的x軸 y軸再去擴充出深度z軸 z 往前為正，向後為負
			\\coordinate (O) at (0,0,0);
			\\coordinate (x) at (7,0,0);
			\\coordinate (y) at 
			(0,7,0);
			\\coordinate (z) at (0,0,7);
			
			\\coordinate (Base1) at (0,0,0);
			\\coordinate (Base2) at (6,0,0);
			\\coordinate (Base3) at (6,6,0);
			\\coordinate (Base4) at (0,6,0);
			\\coordinate (Base1Up) at (0,0,6);
			\\coordinate (Base2Up) at (6,0,6);
			\\coordinate (Base3Up) at (6,6,6);
			\\coordinate (Base4Up) at (0,6,6);
			
			\\coordinate (A) at (Base2);
			\\coordinate (B) at (Base3);
			\\coordinate (C) at (Base4);
			\\coordinate (D) at (Base4Up);
			
			\\draw [draw=black, every edge/.append style={draw=black, dashed}]
			(Base1) edge (Base2)
			(Base2) -- (Base3)
			(Base3) -- (Base4)
			(Base4) edge (Base1)
			(Base1Up) -- (Base2Up)
			(Base2Up) -- (Base3Up)
			(Base3Up) -- (Base4Up)
			(Base4Up) -- (Base1Up)
			(Base1) edge (Base1Up)
			(Base2) -- (Base2Up)
			(Base3) -- (Base3Up)
			(Base4) -- (Base4Up);
			
			\\foreach \\v/\\u/\\t in 
			{ A/left/$A$,
				B/below/$B$,
				C/right/$C$,
				D/right/$D$
			}
			{
				\\draw[ultra thick,fill] (\\v) circle (1.5pt);
				\\node[\\u] at (\\v){\\t};
			}; 
			\\end{tikzpicture}
"""

def runTempTexToPNG(strInputName, strOutName):
    os.chdir(constWorkPath)
    cmdlist = [u'latex %.tex',
               u'dvips %.dvi -E -o %.eps',
               u'convert.exe -density 600 %.eps ' + strOutName]
    for strTemplate in cmdlist:
        timer_start = timeit.default_timer()
        strCmd = strTemplate.replace(u'%', constTempWorkFileMainWordC)
        os.system(strCmd.encode(sys.getfilesystemencoding()))
        timer_end = timeit.default_timer()
        print("Time usage:", timer_end - timer_start, " sec(s)")
        print (strCmd+ u" Completed!!")


class PNGMaker :
    def __init__(self, strTexString, strOutputFilePath):
        self.strTexString = strTexString
        self.strOutputFilePath = strOutputFilePath
        self.tikzSize = str(len(self.strTexString))

        hash_object = hashlib.sha256(self.strTexString.encode('utf-8'))
        hex_dig = hash_object.hexdigest()
        self.tikzHash = unicode(hex_dig)

    def runPNGMaker(self, bCheckHash=True):
        os.chdir(constWorkPath)
        if bCheckHash:
            print("RunPNGMaker Checking....")
            if os.path.isfile(self.strOutputFilePath):
                pic = PILImage.open(self.strOutputFilePath)
                dicMetaData = pic.text
                if dicMetaData.has_key("TikzHash") and dicMetaData.has_key("TikzSize"):
                    if dicMetaData['TikzSize']==self.tikzSize and self.tikzHash ==dicMetaData["TikzHash"]:
                        print(self.strOutputFilePath+" NOT NEED UPDATED!!")
                        return
        print("RunPNGMaker Starting....Please wait")
        timer_start = timeit.default_timer()
        #Write a temp tex file

        with codecs.open(constTempWorkTexFile, "w", "utf-8") as fpt:
            strTemplate = constTempWorkTexTemplate
            strContent = strTemplate.replace("%{{TikzStatment}}", self.strTexString)
            fpt.write(strContent)

        runTempTexToPNG(constTempWorkTexFile, self.strOutputFilePath)

        #加上text tag
        pic = PILImage.open(self.strOutputFilePath)
        metaData = PngImagePlugin.PngInfo()
        metaData.add_text("TikzHash", self.tikzHash, 0)
        metaData.add_text("TikzSize", self.tikzSize, 0)
        pic.save(self.strOutputFilePath, "PNG", pnginfo=metaData)

        timer_end = timeit.default_timer()
        print("Time usage:", timer_end - timer_start, " sec(s)")


def main():
    a = PNGMaker(strTestContent, "testoutput.png")
    a.runPNGMaker()
    pass

if __name__ == '__main__':
    main()