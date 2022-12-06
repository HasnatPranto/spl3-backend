from gensim.models.keyedvectors import KeyedVectors
import numpy as np
import re
from keras.models import load_model
from nltk.corpus import stopwords 

def sent2word(x):
    stop_words = set(stopwords.words('english')) 
    x=re.sub("[^A-Za-z]"," ",x)
    x.lower()
    filtered_sentence = [] 
    words=x.split()
    for w in words:
        if w not in stop_words: 
            filtered_sentence.append(w)
    return filtered_sentence


def makeVec(words, model, num_features):
    vec = np.zeros((num_features,),dtype="float32")
    noOfWords = 0.
    index2word_set = set(model.index_to_key)
    
    for i in words:
        if i in index2word_set:
            noOfWords += 1
            vec = np.add(vec,model[i])        
    vec = np.divide(vec,noOfWords)
    return vec


def getVecs(essays, model, num_features):
    c=0
    essay_vecs = np.zeros((len(essays),num_features),dtype="float32")
    for i in essays:
        essay_vecs[c] = makeVec(i, model, num_features)
        c+=1
    return essay_vecs

def generateScore(content):
  
    num_features = 300
    model = KeyedVectors.load_word2vec_format("word2vecmodel.bin", binary=True)
    clean_test_essays = []
    clean_test_essays.append(sent2word(content))
    testDataVecs = getVecs(clean_test_essays, model, num_features )
    testDataVecs = np.array(testDataVecs)
    testDataVecs = np.reshape(testDataVecs, (testDataVecs.shape[0], 1, testDataVecs.shape[1]))
    lstm_model = load_model("lstm_model_ideal.h5")
    score = lstm_model.predict(testDataVecs)
    
    return round(score[0][0],1) 
    