from collections import Counter
import json

with open ('corpus/segmented.json', 'r', encoding='utf8') as f :
    corpus = json.load(f)


TC:list[str] = []
GA:list[str] = []
for num,content in corpus.items() :
    if content[0] == 'torngcherng' :
        TC.extend(content[2])
    if content[0] == 'gongan' :
        GA.extend(content[2])
tsong = TC + GA

dexTC = Counter(TC)
print(dexTC.most_common(80))

dexGA = Counter(GA)
print(dexGA.most_common(80))

dex = Counter(tsong)
print(dex.most_common(80))
