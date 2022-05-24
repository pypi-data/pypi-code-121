import matplotlib.pyplot as plt  #concern this is in colab context which is oldish

from sklearn.base import BaseEstimator, TransformerMixin

from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler

from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import f1_score#, balanced_accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegressionCV

def hello():
  print('Welcome to AI for Good')
  
import builtins
import types
def up_no_globals(f):
  '''
  A function decorator that prevents functions from looking up variables in outer scope.
  '''
  new_globals = {'__builtins__': builtins} 
  # removing keys from globals() storing global values in old_globals
  for key, val in globals().items():
      if  callable(val):
          new_globals[key] = val
  new_f = types.FunctionType(f.__code__, globals=new_globals, argdefs=f.__defaults__)
  new_f.__annotations__ = f.__annotations__ # for some reason annotations aren't copied over
  return new_f

def up_lottery(student_list):
  random_students = random.sample(student_list, len(student_list))
  table_table = pd.DataFrame(columns=['Table'], index=random_students + ['Blank']*(20-len(student_list)))
  table_table['Table'] = [1]*4 + [2]*4 + [3]*4 + [4]*4 + [5]*4
  return table_table
  
  
def up_get_table(url):
  assert isinstance(url, str), f':Puddles says: Expecting url to be string but is {type(url)} instead.'
  try:
    df = pd.read_csv(url)
  except:
    assert False, f'Puddles says: url is not a legal web site for a table. If using GitHub, make sure to get raw version of file.'
  return df


def up_get_column(table, column_name):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: Expecting a table but instead got a {type(table)}!'
  assert column_name in table.columns.to_list(),f'Puddles says: column_name {column_name} is unrecognized. Check spelling and case. Here are legal column names: {table.columns.to_list()}'

  return table[column_name].to_list()

def up_show_color(rgb_triple):
  assert isinstance(rgb_triple, list) or isinstance(rgb_triple, tuple), f'Puddles says: expecting a list but got {rgb_triple}.'
  assert len(rgb_triple)==3, f'Puddles says: expecting 3 itmes in the list but got {rgb_triple}.'
  assert all([isinstance(x, int) for x in rgb_triple]), f'Puddles says: expecting 3 ints but got {rgb_triple}.'

  plt.imshow([[tuple(rgb_triple)]])
  
def up_plot_against(table, column1, column2):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a pandas dataframe but instead got a {type(table)}!'
  assert column1 in table.columns, f'Puddles says: the first column {column1} is not legal. Check spelling and case. Here are legal columns: {table.columns.to_list()}'
  assert column2 in table.columns, f'Puddles says: the second column {column2} is not legal. Check spelling and case. Here are legal columns: {table.columns.to_list()}'

  if len(set(table[column1].to_list()))>20:
    print(f'Puddles warning: {column1} has more than 20 unique values. Likely to not plot well.')
    
  if len(set(table[column2].to_list()))>5:
    print(f'Puddles warning: {column2} has more than 5 unique values. Likely to not plot well.')

  df = pd.crosstab(table[column1], table[column2])
  ax = df.plot.bar(figsize=[15,8], grid=True)
  try:
    for container in ax.containers:
      ax.bar_label(container)
  except:
    pass

  
def up_table_subset(table, column_name, condition, value):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a pandas dataframe but instead got a {type(table)}!'
  assert isinstance(condition, str), f'Puddles says: condition must be a string but is of type {type(condition)}'
  legal_conditions = {'equals':'==', 'not equals':'!=', '>':'>', '<':'<'}
  assert condition in legal_conditions.keys(), f'Puddles says: condition {condition} incorrect. Must be one of {list(legal_conditions.keys())}'
  assert column_name in table.columns, f'Puddles says: column_name {column_name} is not legal. Check spelling and case. Here are legal columns: {table.columns.to_list()}'
  if 'equals' not in condition and isinstance(value, str):
    assert False, f'Puddles says: expecting value to be a number but is string instead'

  if 'equals' in condition and value not in table[column_name].to_list():
      print(f'Puddles warning: {value} does not appear in {column_name}')

  op = legal_conditions[condition]

  if isinstance(value,int) or isinstance(value,float):
    value = str(value)
  elif isinstance(value,str):
    value = f'"{value}"'
  else:
    assert False, f'Puddles says: tell Steve he has a bug with {value}'

  new_table = table.query(f'`{column_name}`' + op + value)
  if len(new_table)==0:
    print(f'Puddles warning: resulting table is empty')

  return new_table

def up_st_dev(a_list_of_numbers):
  assert isinstance(a_list_of_numbers, list), f'Puddles says: expecting a list but instead got a {type(a_list_of_numbers)}!'
  assert all([not isinstance(x,str) for x in a_list_of_numbers]), f'Puddles says: expecting a list of numbers but list includes a string!'

  st_dev = np.nanstd(a_list_of_numbers)  #ignores nans
  return st_dev

def up_drop_column(table, column_name):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: Expecting a table but instead got a {type(table)}!'
  assert column_name in table.columns.to_list(),f'Puddles says: column_name {column_name} is unrecognized. Check spelling and case. Here are legal column names: {table.columns.to_list()}'

  return table.drop(columns=column_name)

def up_drop_nan_rows(table):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a table but instead got a {type(table)}!'

  dropped_table = table.dropna(axis=0)
  return dropped_table.reset_index(drop=True)

def up_map_column(table, column_name, mapping_dict):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a table but instead got a {type(table)}!'
  assert column_name in table.columns, f'Puddles says: column_name {column_name} is not legal. Check spelling and case. Here are legal columns: {table.columns.to_list()}'
  assert isinstance(mapping_dict, dict), f'Puddles says: expecting mapping_dict to be a dictionary but instead got a {type(mapping_dict)}!'

  column_values = table[column_name].to_list()
  mapping_keys = list(mapping_dict.keys())
  keys_unaccounted = set(mapping_keys).difference(set(column_values))
  if keys_unaccounted:
    print(f'Puddles warning: these keys {keys_unaccounted} do not match any values in the column {column_name}.')

  values_unaccounted = set(column_values).difference(set(mapping_keys))
  if values_unaccounted:
    print(f'Puddles warning: these values {values_unaccounted} are missing a mapping.')

  new_table = table.copy()
  new_table[column_name] = table[column_name].replace(mapping_dict)

  return new_table

def up_get_column_types(table):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a table but instead got a {type(table)}!'

  column_types = []
  for column in table.columns:
    col_list = up_get_column(table, column)
    unique = set(col_list)
    types = [type(x) for x in col_list if not pd.isnull(x)]
    if len(set(types))>1:
      value = [column, 'Mixed', 'Not good']
    else: 
      for item in col_list:
        if pd.isnull(item): continue
        d = type(item)
        if d==str and len(unique)<10:
          value = [column, d.__name__, unique]
        else:
          value = [column, d.__name__, '...']
        break
    column_types.append(value)

  return pd.DataFrame(column_types, columns=['Column', 'Type', 'Unique<10'])

def up_column_histogram(table, column_name):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a table but instead got a {type(table)}!'
  assert column_name in table.columns, f'Puddles says: column_name {column_name} is not legal. Check spelling and case. Here are legal columns: {table.columns.to_list()}'
  assert all([not isinstance(x,str) for x in table[column_name]]), f'Puddles says: the column has string values. Can only plot numeric values.'
  
  table[column_name].plot(kind='hist', figsize=(15,8), grid=True, logy=True)
  
def up_clip_list(value_list, lower_boundary, upper_boundary):
  assert isinstance(value_list, list), f'Puddles says: Expecting a list but instead got a {type(value_list)}!'
  assert all([not isinstance(x,str) for x in value_list]), f'Puddles says: the list has string values. Can only clip numeric values.'
  assert lower_boundary<upper_boundary, f'Puddles says: lower_boundary must be less than upper_boundary!'

  upper_clipped = 0
  lower_clipped = 0
  new_list = []
  for item in value_list:
    if item>upper_boundary:
      value = upper_boundary
      upper_clipped+=1
    elif item<lower_boundary:
      value = lower_boundary
      lower_clipped+=1
    else:
      value = item
    new_list.append(value)
  print(f'Lower items clipped: {lower_clipped}')
  print(f'Upper items clipped: {upper_clipped}')
  return new_list


def up_set_column(table, column_name, new_values):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: Expecting a table but instead got a {type(table)}!'
  assert isinstance(new_values, list), f'Puddles says: Expecting a list but instead got a {type(new_values)}!'
  assert len(new_values)==len(table), f'Puddles says: length of list is {len(new_values)} but length of table is {len(table)}. Mismatch!'
  
  new_table = table.copy()
  new_table[column_name] = new_values
  if column_name not in table.columns.to_list():
    print(f'\n\nPuddles warning: column_name {column_name} is not part of current table so adding new column.\n\n\n')
    new_cols = [column_name] + [col for col in new_table.columns if col != column_name] 
    new_table = new_table[new_cols]
  return new_table


def up_write_table(table, file_name):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: Expecting a table but instead got a {type(table)}!'
  assert isinstance(file_name, str), f'Puddles says: Expecting file_name to be a string but got a {type(file_name)}!'

  if not file_name.endswith('.csv'): file_name += '.csv'
  table.to_csv(file_name, index=False)
  return None

def up_knn(table, new_row, k):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a pandas dataframe but instead got a {type(table)}!'
  assert table.isna().sum().sum()==0, f'Puddles says: table still contains NaN values.'
  for column in table.columns:
    col_list = up_get_column(table, column)
    assert not any([isinstance(x,str) for x in col_list]), f'Puddles says: column {column} contains string values.'
  assert isinstance(new_row, list), f'Puddles says: new_row must be a list but is of type {type(new_row)}'
  assert all([not isinstance(x,str) for x in new_row]), f'Puddles says: expecting a list of numbers but list includes a string!'
  assert isinstance(k, int), f'Puddles says: k must be an integer but is of type {type(k)}'
  assert k>0, f'Puddles says: k must be greater than 0'
  columns = table.columns
  assert len(new_row)==len(columns)-1, f'Puddles says: length of new_row should be {len(columns)-1} but is instead {len(new_row)}.'
  
  last_c = columns[len(columns)-1]
  feature_table = table.drop(columns=last_c)
  labels = table[last_c].to_list()
  assert all([x in [0,1] for x in labels]), f'Puddles says: the target column {last_c} should be binary. Reminder: the target column should be the last column in table.'
  from sklearn.neighbors import KNeighborsClassifier
  neigh = KNeighborsClassifier(n_neighbors=k)
  neigh.fit(feature_table.to_numpy(), labels)
  p = neigh.predict_proba([new_row])
  return [1 if p[0][1]>=.5 else 0, p[0].tolist()]

def up_zip_lists(list1, list2):
  if not isinstance(list1, list):
    try:
      list1 = list(list1)
    except:
      assert False, f'Puddles says: Expecting a list for list1 but instead got a {type(list1)}!'
  if not isinstance(list2, list):
    try:
      list2 = list(list2)
    except:
      assert False, f'Puddles says: Expecting a list for list2 but instead got a {type(list2)}!'
  assert len(list1)==len(list2), f'Puddles says: the lengths of the 2 lists are not equal: {len(list1)}, {len(list2)}.'
  assert len(list1)==len(list2), f'Puddles says: the lengths of the 2 lists are not equal: {len(list1)}, {len(list2)}.'
  
  z = zip(list1, list2)
  result = [[x,y] for x,y in z]
  return result

def up_scale_table(table):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a table but instead got a {type(table)}!'
  num_columns = table.select_dtypes(include=np.number).columns.tolist()  #find columns that are numeric
  all_columns = table.columns.tolist()
  residue = set(all_columns) - set(num_columns)  #any columns that are not numeric?
  assert not residue, f'Puddles says: these columns contain strings {residue}'

  scaler = MinMaxScaler()
  df_scaled = pd.DataFrame(scaler.fit_transform(table), columns=table.columns)
  return df_scaled

def up_apply_3sigma(table, column_name):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expected Dataframe but got {type(table)} instead.'
  assert column_name in table.columns.to_list(), f'Puddles says: unknown column {column_name}'
  assert not any([isinstance(v, str) for v in table[column_name].to_list()]), f'Puddles says: column_name contains strings.'

  df = table.copy()
  m = df[column_name].mean()
  sigma = df[column_name].std()
  df[column_name] = table[column_name].clip(lower=m-3*sigma, upper=m+3*sigma)
  return df

def up_build_decision_tree(table, depth):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a pandas dataframe but instead got a {type(table)}!'
  assert table.isna().sum().sum()==0, f'Puddles says: table still contains NaN values.'
  for column in table.columns:
    col_list = up_get_column(table, column)
    assert not any([isinstance(x,str) for x in col_list]), f'Puddles says: column {column} contains string values.'
  
  assert isinstance(depth, int), f'Puddles says: depth must be an integer but is of type {type(depth)}'
  assert depth>0, f'Puddles says: depth must be greater than 0'
  columns = table.columns

  last_c = columns[len(columns)-1]
  feature_table = table.drop(columns=last_c)
  labels = table[last_c].to_list()
  assert all([x in [0,1] for x in labels]), f'Puddles says: the target column {last_c} should be binary. Reminder: the target column should be the last column in table.'

  from sklearn.tree import DecisionTreeClassifier
  clf = DecisionTreeClassifier(random_state=1234, max_depth=depth)
  clf.fit(feature_table, labels)
  import graphviz
  from sklearn import tree
  # DOT data
  dot_data = tree.export_graphviz(clf, out_file=None, 
                                  feature_names=feature_table.columns,  
                                  class_names=['No', 'Yes'],
                                  filled=True)

  # Draw graph
  graph = graphviz.Source(dot_data, format="png") 
  return graph

def up_list_column_names(table):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a pandas dataframe but instead got a {type(table)}!'
  return table.columns.to_list()

def up_product(value_list):
  assert isinstance(value_list, list)
  assert all([type(v)!=str for v in value_list])
  product = 1
  for v in value_list:
    product *= v
  return product

def up_table_to_list(table):
  return table.to_numpy().tolist()

def up_train_test_split(table, target, test_percentage):
  from sklearn.model_selection import train_test_split
  labels = up_get_column(table, target)
  train_X, test_X, train_y, test_y = train_test_split(table, labels, test_size=test_percentage, shuffle=True,
                                                random_state=1234, stratify=labels)
  return [train_X, test_X]

def up_metrics(zipped_list):
  tp = sum([1 if p==1 and a==1 else 0 for p,a in zipped_list])
  tn = sum([1 if p==0 and a==0 else 0 for p,a in zipped_list])
  fp = sum([1 if p==1 and a==0 else 0 for p,a in zipped_list])
  fn = sum([1 if p==0 and a==1 else 0 for p,a in zipped_list])

  precision = tp/(tp+fp) if (tp+fp)>0 else 0
  recall = tp/(tp+fn) if (tp+fn)>0 else 0
  f1 = 2*precision*recall/(precision+recall) if (precision+recall)>0 else 0
  accuracy = (tp+tn)/len(zipped_list)
  return {'Precision': precision, 'Recall': recall, 'F1': f1, 'Accuracy': accuracy}

def up_metrics_table(metrics_list):
  foo = pd.DataFrame(metrics_list)
  foo.insert(0, 'Threshold', foo.pop('Threshold'))
  return foo

def up_plot_precision_v_recall(metrics_table):
  assert isinstance(metrics_table, pd.core.frame.DataFrame), f'Puddles says: expecting a pandas dataframe but instead got a {type(metrics_table)}!'
  columns = metrics_table.columns.to_list()
  expected = ['Threshold',	'Precision',	'Recall',	'F1',	'Accuracy']
  assert not set(expected) - set(columns), f"Puddles says: expecting columns ['Threshold',	'Precision',	'Recall',	'F1',	'Accuracy'] but got {columns}"
  
  import plotly.express as px
  metrics_table.sort_values(by='Precision', ascending=True, inplace=True)
  fig = px.line(
    data_frame=metrics_table,  
    x='Precision',
    y='Recall',
    title='Precision v. Recall curve',
    hover_data=['Accuracy', 'Threshold', 'F1'])
  fig.update_traces(mode='markers+lines')
  fig.show()
  
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
import tensorflow as tf
from tensorflow import keras

import matplotlib.pyplot as plt

def up_neural_net(train_table, test_table, architecture):
  assert isinstance(train_table, pd.core.frame.DataFrame), f'Puddles says: expecting train_table to be table but instead got a {type(train_table)}!'
  assert isinstance(test_table, pd.core.frame.DataFrame), f'Puddles says: expecting test_table to be table but instead got a {type(test_table)}!'
  assert isinstance(architecture, list) or isinstance(architecture, tuple), f'architecture is a list or tuple, the number of nodes per layer. Instead got {type(architecture)}'
  assert architecture, f'architecture cannot be the empty list'
  assert all([isinstance(x,int) and x>0 for x in architecture]), f'Puddles says: architecture must contain integers greater than 0'


  np.random.seed(seed=1234)
  tf.random.set_seed(1234)

  columns = up_list_column_names(train_table)
  target = columns[-1]
  new_train = train_table.drop(columns=target).to_numpy()
  labels = np.array(up_get_column(train_table, target))
  new_test = test_table.drop(columns=target).to_numpy()
  n = len(columns)-1

  metrics=tf.keras.metrics.BinaryAccuracy(
    name='binary_accuracy', dtype=None, threshold=0.5
  )
  loss=tf.keras.losses.BinaryCrossentropy(from_logits=False)
  learning_rate=.02

  l2_regu = tf.keras.regularizers.L2(0.01)  #weight regularization during gradient descent
  initializer = tf.keras.initializers.HeNormal(seed=1234)  #works best with Relu: https://machinelearningmastery.com/weight-initialization-for-deep-learning-neural-networks/

  early_stop_cb = tf.keras.callbacks.EarlyStopping(
    monitor='loss',
    min_delta=0,
    patience=5,  #Wait 5 epochs for loss to change - if no change, stop
    verbose=0
  )

  model = Sequential()

  #handle first hidden layer separately because of input_dim

  layer_units = architecture[0]
  layer_dropout = .2
  layer_act = 'relu'
  model.add(Dense(units=layer_units, activation=layer_act, activity_regularizer=l2_regu, kernel_initializer=initializer, input_dim=n))  #first hidden layer needs number of inputs
  model.add(Dropout(layer_dropout))

  for layer in architecture[1:]:
    layer_units = layer
    model.add(Dense(units=layer_units, activation=layer_act, activity_regularizer=l2_regu, kernel_initializer=initializer))
    model.add(Dropout(layer_dropout))
    
  #now output layer
  model.add(Dense(units=1, activation='sigmoid'))

  model.compile(loss=loss,
              optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
              metrics=[metrics])
  
  batch = 20
  epochs = 100
  training = model.fit(x=new_train,
                          y=labels,
                          batch_size=batch,
                          epochs=epochs,
                          verbose=0,
                          callbacks=[early_stop_cb])
  print(f'Finished training with {len(training.history["loss"])} epochs ...')

  plt.plot(training.history['binary_accuracy'])
  plt.title('model accuracy')
  plt.ylabel('accuracy')
  plt.xlabel('epoch')
  plt.show()

  np_predictions = model.predict(new_test)

  predictions = [[1-p[0], p[0]] for p in np_predictions]
  print('Finished testing ...')
  return predictions

def up_lower_string_list(string_list):
  result = [c.lower() for c in string_list]
  return result

def up_build_bow(table, text_column, target_column):
  import spacy
  from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
  import string
  from spacy.lang.en import English
  from spacy.lang.en.stop_words import STOP_WORDS
  nlp = spacy.load('en')

  punctuations = string.punctuation
  stop_words = spacy.lang.en.stop_words.STOP_WORDS
  parser = English()

  def spacy_tokenizer(sentence):

      # Creating our token object which is used to create documents with linguistic annotations
      mytokens = parser(sentence)
      
      # lemmatizing each token and converting each token in lower case
      # Note that spaCy uses '-PRON-' as lemma for all personal pronouns lkike me, I etc
      mytokens = [ word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens ]
      
      # Removing stop words
      mytokens = [ word for word in mytokens if word not in stop_words and word not in punctuations]
      
      # Return preprocessed list of tokens
      return mytokens   

  the_text = up_get_column(table, text_column)
  cleaned = [text.strip().lower() for text in the_text]
  vectorizer = CountVectorizer(tokenizer = spacy_tokenizer, ngram_range = (1,1))
  the_bow = vectorizer.fit_transform(cleaned)
  data = the_bow.toarray()
  columns = list(vectorizer.get_feature_names_out())
  bow_table = pd.DataFrame(data, columns=columns)
  bow_table.insert(len(columns), f'__{target_column}__', up_get_column(table, target_column))
  
  return bow_table

def stats_please(*, table):
  assert isinstance(table, pd.core.frame.DataFrame), f'Puddles says: expecting a pandas dataframe but instead got a {type(table)}!'
  return table.describe(include='all').T



