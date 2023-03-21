import requests
from bs4 import BeautifulSoup
import json
import os
import re

#這段代碼總的來說比較短，而且每個網頁總是有微小差別的，所以就沒有作抽象了。每部集子分別用一個函數來處理。

headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'
}

def getFangbao () :
    startlink = 'https://zh.wikisource.org/wiki/%E6%96%B9%E6%9C%9B%E6%BA%AA%E5%85%88%E7%94%9F%E5%85%A8%E9%9B%86_(%E5%9B%9B%E9%83%A8%E5%8F%A2%E5%88%8A%E6%9C%AC)'
    startContent = requests.get(startlink, headers=headers)
    if startContent.status_code != 200:
        raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
    startPar = BeautifulSoup(startContent.text, 'html5lib')
    contentListInHTML = startPar.find('div', {'style': 'column-count:4;-moz-column-count:4;-webkit-column-count:4;width:100%'})
    contentList = []#每一卷及其链接的列表
    for item in contentListInHTML.find_all('a'):
        if item.text == "目録" or item.text == "序" or item.text == "集外文序跋" or item.text == "集外文目録" or item.text == "集外文補遺目録" or item.text == "集外文補遺序" or item.text == "年譜序" or item.text == "年譜" or item.text == "年譜附錄":
            continue
        else:
            contentList.append([item.text, item.get('href')])
    articleList = []
    #获取内容
    for page in contentList :
        pageContent = requests.get(r'https://zh.wikisource.org'+page[1], headers=headers)
        if pageContent.status_code != 200:
            raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
        pagePar = BeautifulSoup(pageContent.text, 'html5lib')
        paragraph = pagePar.find('div', {'style': 'writing-mode:vertical-rl;-moz-writing-mode:vertical-rl;-ms-writing-mode:tb-rl;-webkit-writing-mode:vertical-rl;width:100%;overflow-x:auto;float:right'})
        eachLine = paragraph.find_all('p')
        
        articleName = None
        articleContent = []
        for line in eachLine :
            if line.text[0:2] == '　　':
                if articleName != None :
                    #若發現有標題且不是第一篇，則存儲上一篇
                    if len(''.join(articleContent)) > 5 :
                        articleList.append({'title':articleName, 'content':re.sub('〈[\s\S]*?〉|\\n', '', ''.join(articleContent))})
                        print('已扫描完《%s》。'%articleName)
                articleName = re.sub('〈[\s\S]*?〉|\\n', '', line.text[2:])
                articleContent = []
            elif articleName == None :
                continue
            else :
                articleContent.append(line.text)
        #以下两行是为了加入最后一篇文章
        if len(''.join(articleContent)) > 5 :
            articleList.append({'title':articleName, 'content':re.sub('〈[\s\S]*?〉|\\n', '', ''.join(articleContent))})
            print('已扫描完《%s》。'%articleName)
        print('\n----------已扫描完%s----------\n'%page[0])
    
    with open('corpus/raw/fangBao.json', 'w', encoding='utf-8') as f:
        json.dump(articleList, f, ensure_ascii=False, indent=4)
        
def getLyoudahkwei () :
    def deleComment (raw) :
        kkk = raw
        for span in kkk.find_all('span', {'class': 'inlinecomment'}):
            span.extract()
        return kkk
        
    startlink = 'https://ctext.org/wiki.pl?if=gb&res=110875'
    startContent = requests.get(startlink, headers=headers)
    if startContent.status_code != 200:
        raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
    startPar = BeautifulSoup(startContent.text, 'html5lib')
    contentListInHTML = startPar.find('div', {'class': 'ctext', 'style': 'margin: 10px; '})
    contentList = []#每一卷及其链接的列表
    for item in contentListInHTML.find_all('span', recursive=False):
        contentList.append([item.a.text, item.a.get('href')])
    
    articleList = []
    #获取内容
    for page in contentList :
        pageContent = requests.get(r'https://ctext.org/'+page[1], headers=headers)
        if pageContent.status_code != 200:
            raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
        pagePar = BeautifulSoup(pageContent.text, 'html5lib')
        paragraph = pagePar.find('table', {'style': 'width: 100%;'}).tbody
        eachLine = paragraph.find_all('tr')
        
        articleName = None
        articleContent = []
        for line in eachLine :
            if line.find('td', {'colspan':'2'}) != None:#爲標題
                if articleName != None :
                    #若發現有標題且不是第一篇，則存儲上一篇
                    if len(''.join(articleContent)) > 5 :
                        articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
                        print('已扫描完《%s》。'%articleName)
                articleName = re.sub('\\n', '', line.h2.get('id'))
                articleContent = []
            elif articleName == None :
                continue
            else :
                articleContent.append(deleComment(line.find_all('td', {'class':'ctext'})[-1]).text)
        #以下两行是为了加入最后一篇文章
        if len(''.join(articleContent)) > 5 :
            articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
            print('已扫描完《%s》。'%articleName)
        print('\n----------已扫描完%s----------\n'%page[0])
    
    with open('corpus/raw/LyouDahKwei.json', 'w', encoding='utf-8') as f:
        json.dump(articleList, f, ensure_ascii=False, indent=4)
    
def getYaunaai () :
    startlink = 'https://zh.wikisource.org/wiki/%E6%83%9C%E6%8A%B1%E8%BB%92%E6%96%87%E9%9B%86'
    startContent = requests.get(startlink, headers=headers)
    if startContent.status_code != 200:
        raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
    startPar = BeautifulSoup(startContent.text, 'html5lib')
    contentListInHTML = startPar.find('table', {'class': 'multicol'}).tbody.tr
    contentList = []#每一卷及其链接的列表
    for item in contentListInHTML.find_all('li'):
        contentList.append([item.a.text, item.a.get('href')])
    articleList = []
    #获取内容
    for page in contentList :
        pageContent = requests.get(r'https://zh.wikisource.org'+page[1], headers=headers)
        if pageContent.status_code != 200:
            raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
        pagePar = BeautifulSoup(pageContent.text, 'html5lib')
        paragraph = pagePar.find('div', {'class':'mw-parser-output'})
        eachLine = paragraph.contents
        
        articleName = None
        articleContent = []
        for line in eachLine :
            if line.name == 'h2':
                if articleName != None :
                    #若發現有標題且不是第一篇，則存儲上一篇
                    if len(''.join(articleContent)) > 5 :
                        articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
                        print('已扫描完《%s》。'%articleName)
                articleName = re.sub('\\n', '', line.find('span', {'class':'mw-headline'}).get('id'))
                articleContent = []
            elif articleName == None :
                continue
            elif line.name == 'p':
                articleContent.append(line.text)
        #以下两行是为了加入最后一篇文章
        if len(''.join(articleContent)) > 5 :
            articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
            print('已扫描完《%s》。'%articleName)
        print('\n----------已扫描完%s----------\n'%page[0])
    
    with open('corpus/raw/YauNaai.json', 'w', encoding='utf-8') as f:
        json.dump(articleList, f, ensure_ascii=False, indent=4)

def getYuanhorngdaw () :
    startlink = 'https://ctext.org/wiki.pl?if=gb&res=142162&remap=gb'
    startContent = requests.get(startlink, headers=headers)
    if startContent.status_code != 200:
        raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
    startPar = BeautifulSoup(startContent.text, 'html5lib')
    contentListInHTML = startPar.find('div', {'class': 'ctext', 'style': 'margin: 10px; '})
    contentList = []#每一卷及其链接的列表
    for item in contentListInHTML.find_all('span', recursive=False):
        if item.a.text=='卷之序' or item.a.text=='卷之一】' or item.a.text=='卷之二】' or item.a.text=='卷之三】' or item.a.text=='卷之四】' or item.a.text=='卷之五】' or item.a.text=='卷之六】' or item.a.text=='卷之七】' or item.a.text=='卷之八】' or item.a.text=='卷之九】' :
            continue
        else :
            contentList.append([item.a.text, item.a.get('href')])
    
    articleList = []
    #获取内容
    for page in contentList :
        pageContent = requests.get(r'https://ctext.org/'+page[1], headers=headers)
        if pageContent.status_code != 200:
            raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
        pagePar = BeautifulSoup(pageContent.text, 'html5lib')
        paragraph = pagePar.find('table', {'style': 'width: 100%;'}).tbody
        eachLine = paragraph.find_all('tr')
        
        articleName = None
        articleContent = []
        for line in eachLine :
            if len(line.find_all('td')[-1].text) <= 20:#爲標題
                if articleName != None :
                    #若發現有標題且不是第一篇，則存儲上一篇
                    if len(''.join(articleContent)) > 5 :
                        articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
                        print('已扫描完《%s》。'%articleName)
                articleName = re.sub('\\n', '', line.find_all('td', {'class':'ctext'})[-1].text)
                articleContent = []
            elif articleName == None :
                continue
            else :
                articleContent.append(line.find_all('td', {'class':'ctext'})[-1].text)
        #以下两行是为了加入最后一篇文章
        if len(''.join(articleContent)) > 5 :
            articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
            print('已扫描完《%s》。'%articleName)
        print('\n----------已扫描完%s----------\n'%page[0])
    
    with open('corpus/raw/YuanHorngDaw.json', 'w', encoding='utf-8') as f:
        json.dump(articleList, f, ensure_ascii=False, indent=4)

def getYuanjongdaw () :
    startlink = 'https://zh.wikisource.org/wiki/%E7%8F%82%E9%9B%AA%E9%BD%8B%E9%9B%86'
    startContent = requests.get(startlink, headers=headers)
    if startContent.status_code != 200:
        raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
    startPar = BeautifulSoup(startContent.text, 'html5lib')
    contentListInHTML = startPar.find('ol')#找鏈接列表
    contentList = []#每一卷及其链接的列表
    for item in contentListInHTML.find_all('li'):
        if item.a.text=='卷一' or item.a.text=='卷二' or item.a.text=='卷三' or item.a.text=='卷四' or item.a.text=='卷五' or item.a.text=='卷六' or item.a.text=='卷七' or item.a.text=='卷八' :
            continue
        else :
            contentList.append([item.a.text, item.a.get('href')])
    articleList = []
    #获取内容
    for page in contentList :
        pageContent = requests.get(r'https://zh.wikisource.org'+page[1], headers=headers)
        if pageContent.status_code != 200:
            raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
        pagePar = BeautifulSoup(pageContent.text, 'html5lib')
        paragraph = pagePar.find('div', {'class':'mw-parser-output'})
        eachLine = paragraph.contents
        
        articleName = None
        articleContent = []
        for line in eachLine :
            if line.name == 'h3':
                if articleName != None :
                    #若發現有標題且不是第一篇，則存儲上一篇
                    if len(''.join(articleContent)) > 5 :
                        articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
                        print('已扫描完《%s》。'%articleName)
                articleName = re.sub('\\n', '', line.find('span', {'class':'mw-headline'}).get('id'))
                articleContent = []
            elif articleName == None :
                continue
            elif line.name == 'p':
                articleContent.append(line.text)
        #以下两行是为了加入最后一篇文章
        if len(''.join(articleContent)) > 5 :
            articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
            print('已扫描完《%s》。'%articleName)
        print('\n----------已扫描完%s----------\n'%page[0])
    
    with open('corpus/raw/YuanJongDaw.json', 'w', encoding='utf-8') as f:
        json.dump(articleList, f, ensure_ascii=False, indent=4)

def getYuantsongdaw () :
    startlink = 'https://zh.wikisource.org/zh-hant/%E7%99%BD%E8%98%87%E9%BD%8B%E9%A1%9E%E9%9B%86'
    startContent = requests.get(startlink, headers=headers)
    if startContent.status_code != 200:
        raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
    startPar = BeautifulSoup(startContent.text, 'html5lib')
    contentListInHTML = startPar.find('ul')#找鏈接列表
    contentList = []#每一卷及其链接的列表
    for item in contentListInHTML.find_all('li'):
        if item.a.text=='序' or item.a.text=='卷一' or item.a.text=='卷二' or item.a.text=='卷三' or item.a.text=='卷四' or item.a.text=='卷五' or item.a.text=='卷六' :
            continue
        else :
            contentList.append([item.a.text, item.a.get('href')])
    articleList = []
    #获取内容
    for page in contentList :
        pageContent = requests.get(r'https://zh.wikisource.org'+page[1], headers=headers)
        if pageContent.status_code != 200:
            raise Exception('請求失敗，狀態碼爲 %d' % startContent.status_code)
        pagePar = BeautifulSoup(pageContent.text, 'html5lib')
        paragraph = pagePar.find('div', {'class':'mw-parser-output'})
        eachLine = paragraph.contents
        
        articleName = None
        articleContent = []
        for line in eachLine :
            if line.name == 'h3':
                if articleName != None :
                    #若發現有標題且不是第一篇，則存儲上一篇
                    if len(''.join(articleContent)) > 5 :
                        articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
                        print('已扫描完《%s》。'%articleName)
                articleName = re.sub('\\n', '', line.find('span', {'class':'mw-headline'}).get('id'))
                articleContent = []
            elif articleName == None :
                continue
            elif line.name == 'p':
                articleContent.append(line.text)
        #以下两行是为了加入最后一篇文章
        if len(''.join(articleContent)) > 5 :
            articleList.append({'title':articleName, 'content':re.sub('\\n', '', ''.join(articleContent))})
            print('已扫描完《%s》。'%articleName)
        print('\n----------已扫描完%s----------\n'%page[0])
    
    #with open('corpus/raw/YuanTsongDaw.json', 'w', encoding='utf-8') as f:
    #    json.dump(articleList, f, ensure_ascii=False, indent=4)

getYuantsongdaw ()

print('结束。')
