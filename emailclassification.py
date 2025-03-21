# -*- coding: utf-8 -*-
"""EmailClassification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1puvakMf4NrJJq43-KU_3pR8KOesavgG7
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn

df = pd.read_csv("mail_data.csv")

df.head(10)

## Data Cleaning

df.isna().value_counts()



df['Category'].value_counts()

## Encoding of category
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df['Category'] = le.fit_transform(df['Category'])

## Check the ratio of ham and spam
plt.pie(df['Category'].value_counts(), labels=['ham', 'spam'],autopct = "%0.2f")
plt.show()

## from the above we can infer that the data is imbalance

!pip install imbalanced-learn

# x_sample , y_sample = smote.fit_resample(x,y)
## Now in order to make this data balanced we need to convert the textual data to integer

import nltk
nltk.download('punkt_tab')

df['num_words'] = df['Message'].apply(lambda x : len(nltk.word_tokenize(x)))
df['num_sentences'] = df['Message'].apply(lambda x : len(nltk.sent_tokenize(x)))
df['num_characters'] = df['Message'].apply(lambda x :len(x))

df

# Now we can see that the data is imbalanced
## Now we shall focus on the correlation of the data

sns.heatmap(df.select_dtypes(include = 'int').corr(), annot=True)

"""#Data Preprocessing
1.text to lower case

2.tokenization

3.remove special characters

4.removing stop words and punctuation

5.stemming
"""

from nltk.corpus import stopwords
import nltk
import string
nltk.download('stopwords')

st = stopwords.words('english')
pt = string.punctuation
pt

from nltk import PorterStemmer

ps = PorterStemmer()

def transform_text(text):
  y =[]
  text = text.lower()
  text = nltk.word_tokenize(text)
  for i in text:
    if i.isalnum():
      y.append(i)
  text = y[:]
  y.clear()

  for i in text:
    if (i not in st) and (i not in pt):
      y.append(i)
  text = y[:]
  y.clear()

  for i in text:
    y.append(ps.stem(i))


  return " ".join(y)

## transform_text("hey dancing you do'in? %%%%@@$$$$")

df['transformed_text'] = df['Message'].apply(lambda x : transform_text(x))

df

from wordcloud import WordCloud

wc = WordCloud(width= 500 , height = 500)
spam_wc = wc.generate(df[df['Category']==1]["transformed_text"].str.cat(sep=" "))

plt.imshow(spam_wc)

ham_wc = wc.generate(df[df['Category']==0]['transformed_text'].str.cat(sep=" "))
plt.imshow(ham_wc)

"""## Now vectorization of the transformed_text"""

from sklearn.feature_extraction.text import TfidfVectorizer

tf = TfidfVectorizer()

x_input = tf.fit_transform(df['transformed_text']).toarray()

y = df['Category']

## Randomforest
## SVM
## XGBoost
## naive bayes--> bernoulli , polnomial

df

from imblearn.over_sampling import SMOTE

sm = SMOTE(sampling_strategy = 'minority')
x_sample , y_sample = sm.fit_resample(x_input , y)

plt.pie(y_sample.value_counts() , labels=['ham', 'spam'], autopct="%.2f")

from sklearn.model_selection import train_test_split

x_sample_train , x_sample_test , y_sample_train , y_sample_test = train_test_split(x_sample , y_sample , test_size =0.2)



from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.metrics import accuracy_score , precision_score , confusion_matrix
from sklearn.model_selection import RandomizedSearchCV

# clf = [RandomForestClassifier(), SVC(), XGBClassifier(), GaussianNB(), MultinomialNB(), BernoulliNB()]

## we shall be using randomizedsearchcv since gridsearchcv would be quite complex to compute

models = {
    "RandomForest": RandomForestClassifier(),
    "SVM": SVC(),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
    "GaussianNB": GaussianNB(),
    "MultinomialNB": MultinomialNB(),
    "BernoulliNB": BernoulliNB()
}

# Define hyperparameter grids
param_grids = {
    "RandomForest": {'n_estimators': [50, 100, 200], 'max_depth': [10, 20, None]},
    "SVM": {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']},
    "XGBoost": {'n_estimators': [50, 100], 'max_depth': [3, 5]},
    "GaussianNB": {},  # No hyperparameters to tune
    "MultinomialNB": {'alpha': [0.1, 0.5, 1.0]},
    "BernoulliNB": {'alpha': [0.1, 0.5, 1.0]}
}

# Loop through models and perform GridSearchCV
best_models = {}
for model_name, model in models.items():
    print(f"Training {model_name}...")
    grid = RandomizedSearchCV(model, param_grids[model_name], cv=5, scoring='accuracy', n_jobs=-1)
    grid.fit(x_sample_train, y_sample_train)

    best_models[model_name] = grid.best_estimator_
    print(f"Best params for {model_name}: {grid.best_params_}")

# Evaluate all models
for model_name, model in best_models.items():
    y_pred = model.predict(x_sample_test)
    acc = accuracy_score(y_sample_test, y_pred)
    print(f"{model_name} Accuracy: {acc:.4f}")

## On determining the accuracy of the following algorithms we can check their precision score based on which we can determine the best algorithm to achieve this

svc = SVC(kernel='rbf', C=10)
svc.fit(x_sample_train , y_sample_train)
y_pred = svc.predict(x_sample_test)
precision_score(y_sample_test, y_pred)

rfc = RandomForestClassifier(n_estimators= 100, max_depth= None)
rfc.fit(x_sample_train , y_sample_train)
y_pred2 = rfc.predict(x_sample_test)
precision_score(y_sample_test, y_pred2)

xgb = XGBClassifier(n_estimators = 100, max_depth = 5)
xgb.fit(x_sample_train , y_sample_train)
y_pred3 = rfc.predict(x_sample_test)
precision_score(y_sample_test, y_pred3)

##Support vector machine is getting 100% accuracy and precision score

svc.predict(x_input)

y

import pickle

pickle.dump(tf,open("vectorize.pkl","wb"))
pickle.dump(svc,open("model.pkl","wb"))

pickle.dump(le,open("encoder.pkl","wb"))