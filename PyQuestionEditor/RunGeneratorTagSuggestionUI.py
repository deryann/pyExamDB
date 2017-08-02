#coding=utf-8
#-------------------------------------------------------------------------------
# Name:        使用 Python 語法測試 Xelatex 的時間
# Purpose:
#
# Author:      user
#
# Created:     17/07/2017
# Copyright:   (c) user 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#
#
def runExe():
    """
    Run xelatex.exe -synctex=1 -interaction=nonstopmode "DBExam01all".tex
    """
    import os
    work_path = "E:\\NCTUG2\\Code\\pyExamDBDevUI\\PyQuestionEditor"
    os.chdir(work_path)
    os.system("pyuic4 TagSuggestionConfig.ui -o TagSuggestionConfigWidget.py")

def main():
    import timeit
    print("Runing....Please wait")
    timer_start = timeit.default_timer()
    runExe()
    timer_end = timeit.default_timer()
    print("Time usage:",timer_end - timer_start," sec(s)")
    pass

if __name__ == '__main__':
    main()
