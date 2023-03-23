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
        TC.extend(content[2])

dexTC = Counter(TC)
print(dex.most_common(80))

dexGA = Counter(GA)
print(dex.most_common(80))
