import numpy as np
import nltk
import os
import re
import pickle
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
import pickle

def removeStopWords(essay):
    stop_words = set(stopwords.words('english')) 
    tokens = word_tokenize(essay) 
    filtered_sentence = [] 
    for w in tokens: 
        if w not in stop_words: 
            filtered_sentence.append(w)
    essay = ' '.join(filtered_sentence)
    essay = re.sub("[^A-Za-z ]","",essay)
    
    return essay

def sentenceToword(x):
    x=re.sub("[^A-Za-z0-9]"," ",x)
    words=nltk.word_tokenize(x)
    return words

def noOfWords(essay):
    count=0
    for i in essayToWords(essay):
        count=count+len(i)
    return count

def noOfChar(essay):
    count=0
    for i in essayToWords(essay):
        for j in i:
            count=count+len(j)
    return count

def avgWordLength(essay):
    words = noOfWords(essay)
    if words == 0:
        return 0
    return noOfChar(essay)/words

def noOfSentence(essay):
    return len(essayToWords(essay))

def count_pos(essay):
    sentences = essayToWords(essay)
    noun_count=0
    adj_count=0
    verb_count=0
    adverb_count=0
    for i in sentences:
        pos_sentence = nltk.pos_tag(i)
        for j in pos_sentence:
            pos_tag = j[1]
            if(pos_tag[0]=='N'):
                noun_count+=1
            elif(pos_tag[0]=='V'):
                verb_count+=1
            elif(pos_tag[0]=='J'):
                adj_count+=1
            elif(pos_tag[0]=='R'):
                adverb_count+=1
    
    return noun_count,verb_count,adj_count,adverb_count


def checkMisspell(essay,words):
    essay=essay.lower()
    new_essay = re.sub("[^A-Za-z0-9]"," ",essay)
    new_essay = re.sub("[0-9]","",new_essay)
    count=0
    all_words = new_essay.split()
    for i in all_words:
        if i not in words:
            count+=1
    return count


def essayToWords(essay):
    essay = essay.strip()
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    raw = tokenizer.tokenize(essay)
    final_words=[]
    for i in raw:
        if(len(i)>0):
            final_words.append(sentenceToword(i))
    return final_words

def addAdditionalFeatures(essay,words):
    arr = [] 
    arr.append(noOfChar(essay))
    arr.append(noOfWords(essay))
    arr.append(noOfSentence(essay))
    arr.append(avgWordLength(essay))
    arr.append(checkMisspell(essay,words))
    pos = np.asarray(count_pos(essay))
    arr = np.asarray(arr)
    combined = np.concatenate((arr,pos),axis=None)
    
    return combined

def getSystemScore(essay):
    reference_path = os.getcwd()+'\\api\\ml_models\\reference.txt'
    ml_model_path = os.getcwd()+'\\api\\ml_models\\RF_with_PP'
    vector_path = os.getcwd()+'\\api\\ml_models\\vector_additional.pickle'
    
    data = open(reference_path).read()
    words = re.findall('[a-z]+', data.lower())
    cleanedEssay = removeStopWords(essay)

    additionalFeatures = addAdditionalFeatures(cleanedEssay,words)
    
    cv = pickle.load(open(vector_path,"rb"))
    data = [cleanedEssay]
    vectorized = cv.transform(data).toarray()
    vectorized = np.concatenate((additionalFeatures,vectorized),axis=None)
    vectorized = np.array([vectorized])

    ml_model = pickle.load(open(ml_model_path,'rb'))
    predictedScore = ml_model.predict(vectorized)
    
    return predictedScore[0]