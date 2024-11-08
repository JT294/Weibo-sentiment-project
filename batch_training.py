import pandas as pd
import os
import numpy as np
from gensim.models import KeyedVectors
from sklearn.utils import shuffle
import jieba

from tensorflow.keras.layers import Input, Dense, LSTM, Conv1D,Dropout,Bidirectional,Multiply,Embedding,MaxPooling1D,ConvLSTM2D,Conv2D,MaxPooling2D
from tensorflow.keras.models import Model
import tensorflow.keras.backend as K
# below bag may have different path 
from tensorflow.python.keras.layers.merge import concatenate  
from tensorflow.python.keras.layers.core import *
from tensorflow.python.keras.layers.recurrent import LSTM
from tensorflow.keras.models import *
from tensorflow.keras.utils import to_categorical

## load embedding
wv_from_text = KeyedVectors.load_word2vec_format('./tencent-ailab-embedding-zh-d100-v0.2.0-s/tencent-ailab-embedding-zh-d100-v0.2.0-s.txt', binary=False)
## load training data
pd_all = pd.read_csv("weibo_senti_100k.csv")
pd_all = shuffle(pd_all)
x_data, y_data = pd_all.review.values, pd_all.label.values

## global factor
CONTENT_LEN = 50
INPUT_DIMS = wv_from_text.vector_size
TIME_STEPS = CONTENT_LEN
lstm_units = 64
bs = 100

## Tokenize word
with open('stopwords.txt','r',encoding='utf-8') as f:
    stopwords = f.readlines()
    stopwords = [x.rstrip() for x in stopwords]

## padding the sentence
all_content = []
for i in range(x_data.shape[0]):
    content_i = jieba.lcut(x_data[i])
    ## cut text or padding
    if len(content_i) > CONTENT_LEN:
        content_i = content_i[:CONTENT_LEN]
    elif len(content_i) < CONTENT_LEN:
        for _ in range(CONTENT_LEN-len(content_i)):
            content_i.append('</s>')
    ## add current review to all_content(n_observations,sentence_length)
    all_content.append(content_i)

SINGLE_ATTENTION_VECTOR = False
def attention_3d_block(inputs):
    # inputs.shape = (batch_size, time_steps, input_dim)
    input_dim = int(inputs.shape[2])
    a = inputs
    a = Dense(input_dim, activation='softmax')(a)
    if SINGLE_ATTENTION_VECTOR:
        a = Lambda(lambda x: K.mean(x, axis=1), name='dim_reduction')(a)
        a = RepeatVector(input_dim)(a)
    a_probs = Permute((1, 2), name='attention_vec')(a)

    output_attention_mul = concatenate([inputs, a_probs], name='attention_mul')
    return output_attention_mul

def em_attention_model():
    inputs = Input(shape=(CONTENT_LEN, INPUT_DIMS))

    embedder = Embedding(x_data.shape[0]//bs+1,CONTENT_LEN,trainable = False)
    embed = embedder(inputs)

    x = Conv1D(filters = 64, kernel_size = 1, activation = 'relu')(inputs)  #, padding = 'same'
    x = Dropout(0.3)(x)

    #lstm_out = Bidirectional(LSTM(lstm_units, activation='relu'), name='bilstm')(x)
    #对于GPU可以使用CuDNNLSTM
    lstm_out = Bidirectional(LSTM(lstm_units, return_sequences=True))(x)
    lstm_out = Dropout(0.3)(lstm_out)
    attention_mul = attention_3d_block(lstm_out)
    attention_mul = Flatten()(attention_mul)

    output = Dense(2, activation='softmax')(attention_mul)
    model = Model(inputs=[inputs], outputs=output)
    return model

m = em_attention_model()
m.summary()
m.compile(optimizer='adam', loss='categorical_crossentropy',metrics=['accuracy'])

# bs = 10
for k in range(bs):
    index_start = len(all_content)//bs*k
    index_end = len(all_content)//bs*(k+1)
    batch_content = all_content[index_start:index_end]
    b_y_data = y_data[index_start:index_end]
    b_x_data = x_data[index_start:index_end]

    ## vectorize each word
    v_a_content = np.empty((len(batch_content),CONTENT_LEN,wv_from_text.vector_size),dtype='float')
    for i in range(len(batch_content)):
        for j in range(CONTENT_LEN):
            ## if current word in ailab, convert to vector
            try:
                v_a_content[i][j] = list(wv_from_text.get_vector(batch_content[i][j]))
            ## otherwise, add the first char's vector
            except:
                v_a_content[i][j] = list(wv_from_text.get_vector('</s>'))

    # v_a_content.shape
    y = to_categorical(b_y_data)


    m.fit(v_a_content,y, epochs=5,batch_size=64, validation_split=0.1)

m.save("./model.h5")

preds = m.evaluate(v_a_content,y)
from sklearn.metrics import classification_report
print(classification_report(preds,y))


