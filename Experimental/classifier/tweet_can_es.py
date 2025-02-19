# -*- coding: utf-8 -*-

import nltk
import csv
import random
import codecs
import re
from nltk.corpus import stopwords

stopset = list(set(stopwords.words('spanish')))
hil_tweets = []
trump_tweets = []
bernie_tweets = []
cruz_tweets = []
classes = {}

def transform(temp):
    if temp == "imo":
        return "opinion"
    elif temp == "inches":
        return "inch"
    elif temp == "including" or temp == "included" or temp == "includes":
        return "include"
    elif temp == "issued" or temp == "issues":
        return "issue"
    elif temp == "ppl":
        return "people"
    elif temp == "prices":
        return "price"
    elif temp == "say":
        return "says"
    elif temp == "shocked" or temp == "shocker" or temp == "shocking":
        return "shock"
    #elif temp == "sooooo" or temp == "soooo" or temp == "sooo" or temp == "soo":
    #    return "so"
    return temp

def getPureWord(word):
    #if str.startswith(word,'@'):
    #   return ""
    #print word
    temp = word.lower()
    if str.startswith(temp,"http"):
        return ""
    temp = ''.join(e for e in temp if e.isalpha()) 
    #if temp not in stop_words and temp !='':
    if temp not in stopset and temp !='':
        return transform(temp)
    else:
        return ""

def purifyText(input):
    output = input.replace('\r','').replace('\n','')
    op = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', output)
    op1 = " ".join(getPureWord(w) for w in op.split())
    return op1.strip()


def buildHash():
    #Hillary, Bernie, Trump, Cruz, GOP, DEM 
    classes["trump"] = ["donald","trump","donaldtrump"]
    classes["cruz"] = ["tedcruz","cruz","ted"]
    classes["hillary"] = ["hillaryclinton","hillary","clinton"]
    classes["bernie"] = ["berniesanders","bernie","sanders","bern"]
    classes["gop"] = ["gop","gopdebate","republicans"]
    classes["dem"] = ["dem","demdebate","democrats","Democratic","democrata","democrat"]


def getEntities(line):
    line = line.lower()
    op = set()
    for key in classes:
        temp = classes[key]
        #print temp
        for t in temp:
            #print type(line)
            if t.lower() in line:
                op.add(key)
            if key in op:
                break
    return list(op)


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


# Process Tweet
def processTweet(tweet):
    tweet = tweet.lower()
    # Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
    # Convert @username to AT_USER
    tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
    # Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    # Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    # trim
    tweet = tweet.strip('\'"')
    return tweet


def tweet_word(words):
    return dict([(word.decode('utf-8'), True) for word in words.split() if word.decode('utf-8') not in stopset])


buildHash()
test_set = []

for x in ['a', 'b', 'c', 'd', 'e']:
#for x in ['annotatedTrump2.csv']:
    with codecs.open('../python/Annotated4/annotated.csva' + x, 'rb') as csvfile:
        tweets = csv.reader(csvfile, delimiter=',', quotechar='\'')
        for tweet in tweets:
            if tweet[12] == 'berniePositive':
                bernie_tweets.append(purifyText(tweet[13]))
            elif tweet[12] == 'hillaryPositive':
                hil_tweets.append(purifyText(tweet[13]))
            elif tweet[12] == 'cruzPositive':
                cruz_tweets.append(purifyText(tweet[13]))
            elif tweet[12] == 'trumpPositive':
                trump_tweets.append(purifyText(tweet[13]))
            elif tweet[12] == 'nuetral':
                test_set.append(tweet)



labeled_words = ([(word, 'hillary') for word in hil_tweets] + [(word, 'trump') for word in trump_tweets] + [(word, 'cruz') for word in cruz_tweets] + [(word, 'bernie') for word in bernie_tweets])
random.shuffle(labeled_words)

featuresets = [(tweet_word(n), classify) for (n, classify) in labeled_words]

train_set = featuresets

# Generating Test Set...
'''
for x in ['testTrump.csv']:
    with codecs.open('../python/annotated2/' + x, 'rb') as csvfile:
        tweets = csv.reader(csvfile, delimiter=',', quotechar='\'')
        for tweet in tweets:
            if tweet[7] == '0':
                test_set.append(tweet)
'''

# Ref - http://www.nltk.org/api/nltk.classify.html
# ALGORITHMS = ['GIS', 'IIS', 'MEGAM', 'TADM']
algorithm = nltk.classify.MaxentClassifier.ALGORITHMS[1]
classifier = nltk.MaxentClassifier.train(train_set, algorithm, max_iter=3)
classifier.show_most_informative_features(10)

#print(nltk.classify.accuracy(classifier, test_set))

i = 1
with open("canoutput.csv", 'wb') as f:
    for tweet in test_set:
        op1 = purifyText(tweet[13])
        op = getEntities(op1)
        if "trump" in op or "bernie" in op or "hillary" in op or "cruz" in op:
            result = classifier.classify(tweet_word(op1))
            print tweet[13]
            print result
        #else:
        #    print result + "Positive"
        i += 1
        if i > 100:
            break

