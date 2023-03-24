import json
import numpy as np

with open ('corpus/segmented.json', 'r', encoding='utf-8') as f :
    corpus = json.load(f)

with open ('stopWords.json', 'r', encoding='utf-8') as f :
    stopWords:list[str] = json.load(f)


def stop (raw:dict) -> dict :
    #輸入爲分詞文檔，應輸出相同的東西，但去除停用詞。
    newDict:dict = {}
    for key,value in raw.items() :
        cooked = [word for word in value[2] if word not in stopWords]
        newDict[key] = [value[0], value[1], cooked]
    return newDict

def list2str (raw:dict) -> dict :
    ripe:dict = {}
    for key, value in raw.items() :
        ripe[key] = [value[0], value[1], ' '.join(value[2])]
    return ripe


doc_train = doc_test = sect_train = sect_test = author_train = author_test = None
def seperate (raw:dict) :
    '''
    從文檔列表劃分訓練集和測試集，返回派別、作者、詞袋的訓練集與測試集。
    '''
    doc = []
    sect = []
    author = []
    for content in raw.values() :
        doc.append(content[2])
        sect.append(content[0])
        author.append(content[1])
    from sklearn.model_selection import train_test_split
    global doc_train, doc_test, sect_train, sect_test, author_train, author_test
    doc_train, doc_test, sect_train, sect_test, author_train, author_test = train_test_split(doc, sect, author, test_size=0.3, random_state=10023, shuffle=True)
    #doc_train, doc_test, sect_train, sect_test = train_test_split(doc, sect, test_size=0.3, random_state=10023, shuffle=True)

def makeVector (fang:str) :
    global doc_train, doc_test
    if fang == 'TFIDF' :
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(ngram_range=(1, 1)).fit(doc_train)
        doc_train = vectorizer.transform(doc_train).toarray()
        doc_test = vectorizer.transform(doc_test).toarray()
    if fang == 'BAG' :
        from sklearn.feature_extraction.text import CountVectorizer
        vectorizer = CountVectorizer(ngram_range=(1, 1)).fit(doc_train)
        doc_train = vectorizer.transform(doc_train).toarray()
        doc_test = vectorizer.transform(doc_test).toarray()
    return doc_train, doc_test

def sift (fang:str, x_train, x_test, y_train, topN:int=1000, threshold=0.0002) :
    '''
    topN爲互信息篩選特徵數量，threshold爲方差篩選閾值
    '''
    if fang == 'mutual_info' :
        #互信息
        from sklearn.feature_selection import mutual_info_classif
        feature_scores = mutual_info_classif(x_train, y_train, random_state=0)
        high_score_features_ind = np.argpartition(feature_scores, -topN)[-topN:]
        x_train = x_train[:,high_score_features_ind]
        x_test = x_test[:,high_score_features_ind]
    if fang == 'variance' :
        #方差筛选
        from sklearn.feature_selection import VarianceThreshold
        selector = VarianceThreshold(threshold=threshold)
        sel = selector.fit(x_train)
        sel_index = sel.get_support()
        #print(np.sum(sel_index==False))
        #print(np.sum(sel_index==True))
        x_train = x_train[:,sel_index]
        x_test = x_test[:,sel_index]
    return x_train, x_test

def classify (x_train, y_train, x_test, y_test, algorithm) :
    if algorithm == 'SVM' :
        from sklearn.svm import SVC, LinearSVC
        clf = SVC(probability=True, kernel='linear').fit(x_train, y_train)
    if algorithm == 'randomForest' :
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(max_depth=2, random_state=0).fit(x_train, y_train)
    if algorithm == 'log' :
        from sklearn.linear_model import LogisticRegression
        clf = LogisticRegression(solver="liblinear", random_state=0).fit(x_train, y_train)
    if algorithm == 'bayes' :
        from sklearn.naive_bayes import GaussianNB
        clf = GaussianNB().fit(x_train, y_train)
    if algorithm == 'kNeighbour' :
        from sklearn.neighbors import KNeighborsClassifier
        clf = KNeighborsClassifier(n_neighbors=5).fit(x_train, y_train)
    if algorithm == 'tree' :
        from sklearn import tree
        clf = tree.DecisionTreeClassifier().fit(x_train, y_train)
    classified = clf.predict(x_test)
    print('訓練好了一個模型。')
    return classified

def report (x_train, y_train, x_test, y_test, y_classified) :
    from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score
    print(classification_report(y_test, clf.predict(x_test),digits=8))
    print(confusion_matrix(y_test, clf.predict(x_test)))
    print(roc_auc_score(y_test, clf.predict(x_test)))


def main (ifStop:bool, repre:str, ifSift=False, algo=None) :
    global doc_train, doc_test, sect_train, sect_test, author_train, author_test, corpus
    if ifStop == True :
        corpus = stop(corpus)
    corpus = list2str(corpus)
    seperate(corpus)
    doc_train, doc_test = makeVector (repre)
    if ifSift != False :
        doc_train, doc_test = sift (ifSift, doc_train, doc_test, sect_train)
    print('完成降維')
    sect_classified = classify(doc_train, sect_train, doc_test, sect_test, algo)
    report (doc_train, sect_train, doc_test, sect_test, sect_classified)
    

if __name__ == '__main__' :
    main(False, 'TFIDF', 'mutual_info', 'bayes')