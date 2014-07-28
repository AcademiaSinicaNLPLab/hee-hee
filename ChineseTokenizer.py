# coding: utf-8

## install required packages
## jieba: http://www.oschina.net/p/jieba
# > pip install jieba

### jianfan
## translation between traditional and simplified chinese
## https://code.google.com/p/python-jianfan/
# > sudo easy_install -n jianfan


import jieba
import jianfan

class ChineseTokenizer(object):
    """
    docstring for Tokenizer
    """
    def __init__(self):
        self.result = None
        
    def tokenize(self, text):

        ## detect chs or cht
        ## ...
        pass

        ## translate to simplified chinese
        text_chs = jianfan.ftoj(text)

        ## cut by jieba
        res_chs = list(jieba.cut(text_chs)) ## res: [u'\u6211', u'\u6765\u81ea', u'\u53f0\u6e7e']

        ## convert to cht
        res_cht = map(lambda x: jianfan.jtof(x), res_chs)

        self.result = res_cht

        return res_cht

if __name__ == '__main__':
    
    ctknz = ChineseTokenizer()

    text = '我在臺灣清華大學念碩士'
    res = ctknz.tokenize(text)

    print '/ '.join(res)

# sent_cht = '我來自臺灣，我在哈佛大學念書'
# print sent_chs ## 我来自台湾  
# sent_chs = '小明硕士毕业于中国科学院计算所，后在日本京都大学深造'

## 我(Nh)　來自(VJ)　臺灣(Nc)　，(COMMACATEGORY)
## 我(Nh)　在(P)　哈佛(Nb)　大學(Nc)　念書(VA)


## 小明/ 碩士/ 畢業/ 於/ 中國科學院/ 計算所/ ，/ 後/ 在/ 日本京都大學/ 深造

## 小明(Nb)　碩士(Na)　畢業(VH)　於(P)　中國(Nc)　科學院(Nc)　計算(VC)　所(D)　，(COMMACATEGORY)
## 後(Ncd)　在(P)　日本(Nc)　京都(Nc)　大學(Nc)　深造(VA)
