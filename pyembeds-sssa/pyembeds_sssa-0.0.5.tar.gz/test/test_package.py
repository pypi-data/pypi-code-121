from pyembeds.data.load_data import load_capythone_data

print('='*5, 'TESTING LOAD CAPYTHONE DATA', '='*5)
data = load_capythone_data()
reviews = data['reviews']
positive_word = data['positive_word']
negative_word = data['negative_word']

print('reviews loaded:', len(reviews))
print('positive_word loaded:', len(reviews))
print('negative_word loaded:', len(negative_word))

from pyembeds.data.load_data import load_wordcloud_ita_data
print('='*5, 'TESTING LOAD WORDCLOUD DATA', '='*5)
data = load_wordcloud_ita_data()
text = data['manzoni']
stop_words = data['stopwords_italian']
print('text len loaded:', len(text))
print('stopwords_italian loaded:', len(stop_words))


#pip uninstall pyembeds-sssa

