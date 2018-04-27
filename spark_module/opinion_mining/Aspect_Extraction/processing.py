#!/usr/bin/env python
# from nltk.corpus import stopwords

# from textblob import TextBlob
from nltk.corpus import wordnet as wn
from nltk.parse.stanford import StanfordDependencyParser
import codecs
import re
import cat_dict
path_to_jar = '/Users/payoj/Downloads/stanford-corenlp-full-2018-02-27/stanford-corenlp-3.9.1.jar'
path_to_models_jar = '/Users/payoj/Downloads/stanford-corenlp-full-2018-02-27/stanford-corenlp-3.9.1-models.jar'
dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)


word_to_categories = cat_dict.category_dict()


def process_tweet(tweet):
    new_tweet = re.sub(r'^https?:\/\/.*[\r\n]*', '', tweet)
    new_tweet = new_tweet.replace('!', '.').replace('?', '.')
    new_tweet = re.sub(r'#(\w+)', '', tweet)
    new_tweet = re.sub(r'\.\.+', '.', new_tweet)
    return new_tweet


def parsing(tweet):
    print(tweet)
    result = dependency_parser.raw_parse(tweet)
    dep = list(result)[0]
    depend_parser = list(dep.triples())
    return depend_parser


def get_term(parsed_list):
    aspect_term = {'NN': [], 'JJ': []}
    for relation in parsed_list:

        if relation[1] == 'amod' or relation[1] == 'advmod':  # Adj/ adv as aspect aspect_term

            if relation[2][1] == 'JJ' and relation[0][1] != 'RB':
                aspect_term['NN'].append((relation[0][0], relation[2][0]))
                aspect_term['JJ'].append(relation[2][0])
            else:
                aspect_term['NN'].append((relation[2][0], relation[0][0]))
                aspect_term['JJ'].append(relation[0][0])

        if relation[1] == 'dobj' or relation[1] == 'nsubj':  # Make noun as aspect term. // check for auxiliary verb
            for i, term in enumerate(relation):
                if term[1] == 'NN':
                    aspect_term['NN'].append((term[0], relation[2 - i][0]))
                if term[1] == 'JJ':
                    aspect_term['JJ'].append(term[0])
        if relation[1] == 'advcl':
            aspect_term['JJ'].append(relation[2][0])
        if relation[1] == 'xcomp':
            aspect_term['JJ'].append(relation[0][0])
            aspect_term['JJ'].append(relation[2][0])
    aspect_term['JJ'] = list(set(aspect_term['JJ']))

    for rel in parsed_list:
        if rel[1] == 'conj' and rel[0][0] in aspect_term:
            if rel[0][1] == 'JJ':
                aspect_term.append(rel[2][0])

    aspect_term['JJ'] = list(set(aspect_term['JJ']))

    return aspect_term


def get_aspect_category(aspect_term):
    tweet_aspect_categories = dict()

    adj_aspect = aspect_term['JJ']
    filtered_noun_aspects = [(aspect, describing_word) for aspect, describing_word in aspect_term['NN']
                             if describing_word in adj_aspect]

    for aspect, describing_word in filtered_noun_aspects:

        print('Aspect, word', aspect, describing_word)

        if describing_word in word_to_categories and len(word_to_categories[describing_word]) > 0:
            max_score, max_score_index = max_similarity_score_and_index(aspect, word_to_categories[describing_word])
            if max_score > 0:
                overall_aspect_category = word_to_categories[describing_word][max_score_index]
                tweet_aspect_categories[overall_aspect_category] = tweet_aspect_categories.get(overall_aspect_category, []) + [aspect]

    return tweet_aspect_categories


def max_similarity_score_and_index(aspect_term, aspect_categories):
    max_score = 0
    max_score_index = -1
    for index, aspect_category in enumerate(aspect_categories):
        score = detect_similarity(aspect_term, aspect_categories)
        if score > max_score:
            max_score = score
            max_score_index = index
    return max_score, max_score_index


def detect_similarity(aspect_term, aspect_category):
    print(aspect_term, aspect_category)
    try:
        aspect_vector = wn.synsets(aspect_term)[0]
    except:
        return 0

    aspect_category_vector = wn.synsets(aspect_category)[0]
    sim_score = wn.wup_similarity(aspect_category_vector, aspect_vector)
    print(sim_score)
    if sim_score is not None and sim_score >= 0:
        return sim_score
    return 0


def get_aspect_sentiment(adj):
    sentiment_score = textblob.TextBlob(adj).sentiment.polarity
    return sentiment_score


def get_category_sentiment(aspect_dict):
    aspect_category_sentiment = {}
    for cat in aspect_dict:
        score = 0
        for word in aspect_dict[cat]:
            score += get_aspect_sentiment(word)
        if score > 0:
            aspect_category_sentiment[cat] = 'Positive: ' + str(score)
        if score < 0:
            aspect_category_sentiment[cat] = 'Negative: ' + str(score)
        else:
            aspect_category_sentiment[cat] = 'Neutral: ' + str(score)

    return aspect_category_sentiment


tweets = []
f = codecs.open('example.txt', 'r', encoding='utf-8')
for line in f:
    line = line.strip()
    tweets.append(line)
    break
f.close()

for tweet in tweets:
    processed_tweet = process_tweet(tweet)
    relation = parsing(processed_tweet)
    aspects = get_term(relation)
    if aspects != {}:
        category = get_aspect_category(aspects)
# tweet_category_sentiment = get_category_sentiment(category)
# print(tweet_category_sentiment)
# print(category)
