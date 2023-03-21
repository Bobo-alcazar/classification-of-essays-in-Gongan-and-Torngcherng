from jiayan import load_lm
from jiayan import CRFSentencizer
lm = load_lm('jiayan.klm')
from ltp import LTP
ltp = LTP('D:/LTP/base2')


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
