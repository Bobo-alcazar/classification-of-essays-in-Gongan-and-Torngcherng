from jiayan import load_lm
from jiayan import CRFSentencizer
from jiayan import CharHMMTokenizer
lm = load_lm('jiayan.klm')
from ltp import LTP
ltp = LTP('D:/LTP/base2')
import json


punc = ['，','。','；','“','”','「','」','‘','’','『','』','.','《','》','〈','〉','、','/','／','？','！']

def sentenceSegmentation (paragraph:str, includePunctuation:bool) ->list[str] :
    '''
    將成段文本斷爲一句一句，以列表返回。
    includePunctuation參數表示原文本是否具有（現代）標點，據此將採用不同的模型來處理。
    '''
    if includePunctuation == True :
        #如果是有標點文本，就採用LTP分句
        from ltp import StnSplit#有標點分句
        segmented:list[str] = StnSplit().split(paragraph)
    elif includePunctuation == False :
        #如果是無標點文本，則採取jiayan分句
        sentencizer = CRFSentencizer(lm)
        sentencizer.load('cut_model')
        segmented:list[str] = sentencizer.sentencize(paragraph)
    return segmented

def wordSegmentation (sentences:list[str], model:str) -> list[str] :
    '''
    傳入句子列表，傳出詞袋列表
    '''
    if model = 'jiayan' :
        tokenizer = CharHMMTokenizer(lm)#隱馬爾可夫模型分詞
        wordBag:list[str] = []
        for sentence in sentences :
            segmentedSentence = tokenizer.tokenize(sentence)
            wordBag.extend(segmentedSentence)
        wordBag = [word for word in wordBag if word not in punc]#清除標點符號
    return wordBag

def excution (articleList:list, phay:str, name:str) :
    personalList:list[list] = []
    for article in articleList :
        segmented = wordSegmentation(sentenceSegmentation(article['content']))
        info = [phay, name, segmented]
        totalCorpus[num] = info
        num += 1

if __name__ == '__main__' :
    num = 1
    totalCorpus:dict = dict()
    with open('raw/fangBao.json', 'r', encoding='utf-8') as f:
        excution (json.load(f), 'torngcherng', 'FangBao')
    with open('raw/LyouDahKwei.json', 'r', encoding='utf-8') as f:
        excution (json.load(f), 'torngcherng', 'LyouDahKwei')
    with open('raw/YauNaai.json', 'r', encoding='utf-8') as f:
        excution (json.load(f), 'torngcherng', 'YauNay')
    with open('raw/YuanHorngDaw.json', 'r', encoding='utf-8') as f:
        excution (json.load(f), 'torngcherng', 'YuanHorngDaw')
    with open('raw/YuanJongDaw.json', 'r', encoding='utf-8') as f:
        excution (json.load(f), 'torngcherng', 'YuanJongDaw')
    with open('raw/YuanTsongDaw.json', 'r', encoding='utf-8') as f:
        excution (json.load(f), 'torngcherng', 'YuanTsongDaw')