# -*- coding: utf-8 -*-

from algoliasearch import algoliasearch
from babelnet_client import BabelNetClient

from sqlalchemy.orm import sessionmaker, load_only
from crawler.models import Ingredients, db_connect as pg_db_connect
from foodb.models import Foods, db_connect as mysql_db_connect

import re

#client = algoliasearch.Client("P0Y1SRPNG9", "f5db240398a9131e58d29687a96a88c1")
#index = client.init_index('food')

#index.set_settings({
#        "searchableAttributes": ["title", "ingredients"],
#        "attributesForFaceting": ["ingredients", "no_cook", "total_time", "source"],
#        "customRanking": ["desc(rating)"]
#    }, True)

i = 0

engine = mysql_db_connect()
Session = sessionmaker(bind=engine)
session = Session()

pg_engine = pg_db_connect()
Pg_Session = sessionmaker(bind=pg_engine)
pg_session = Pg_Session()

def parse_line(line):
    words = []
    word = None
    endchar = None
    for char in line:
        if word is None:
            if char == '<':
                word = char
                endchar = '>'
            elif char == '"':
                word = char
                endchar = '"'
        else:
            word += char
            if char == endchar:
                words.append(word)
                word = None
    return words

q = session.query(Foods).offset(400).limit(600).options(load_only("id", "name", "wikipedia_id"))

wikipedia_ids = {}
for r in q:
    item = {
        'food': r,
        'ingredient': pg_session.query(Ingredients).filter(Ingredients.foodb_id==r.id).first(),
    }
    if item['ingredient'] is None:
        item['ingredient'] = Ingredients(name=r.name, foodb_id=r.id, french_labels=[])
    wikipedia_ids['<http://dbpedia.org/resource/' + (r.wikipedia_id if r.wikipedia_id is not None else str(r.id)) + '>'] = item
print wikipedia_ids.keys()

commons_wikipedia_ids = {}
french_wikipedia_ids = {}
with open('interlanguage_links_en.tql', 'r') as interlanguage:
    for line in interlanguage:
        if line.startswith('<'):
            line = parse_line(line)
            if len(line) == 4 and line[0] in wikipedia_ids:
                food = wikipedia_ids[line[0]]

                if line[2].startswith('<http://commons.dbpedia.org/resource/'):
                    commons_wikipedia_ids[line[2]] = food
                    food['commons_wikipedia_id'] = line[2][37:-1]
                    print "FRENCH ", food['food'].wikipedia_id, food['commons_wikipedia_id']
                elif line[2].startswith('<http://fr.dbpedia.org/resource/'):
                    french_wikipedia_ids[line[2]] = food
                    food['french_wikipedia_id'] = line[2][32:-1]
                    print "FRENCH ", food['food'].wikipedia_id, food['french_wikipedia_id']

with open('interlanguage_links_fr.tql', 'r') as interlanguage:
    for line in interlanguage:
        if line.startswith('<'):
            line = parse_line(line)
            if len(line) == 4:
                if line[2] in wikipedia_ids and line[0].startswith('<http://fr.dbpedia.org/resource/'):
                    food = wikipedia_ids[line[2]]
                    french_wikipedia_ids[line[0]] = food
                    food['french_wikipedia_id'] = line[0][32:-1]
                    print("FR EN", food['food'].wikipedia_id, food['french_wikipedia_id'])
                elif line[2] in commons_wikipedia_ids and line[0].startswith('<http://fr.dbpedia.org/resource/'):
                    food = commons_wikipedia_ids[line[2]]
                    french_wikipedia_ids[line[0]] = food
                    food['french_wikipedia_id'] = line[0][32:-1]
                    print("FR CO", food['food'].wikipedia_id, food['french_wikipedia_id'])
            else:
                print("ERROR FR", line)

with open('labels_fr.tql', 'r') as labels:
    for line in labels:
        if line.startswith('<'):
            line = parse_line(line)
            if len(line) == 4:
                if line[0] in french_wikipedia_ids:
                    print "label", line[2]
                    food['ingredient'].french_labels.append(line[2])
            else:
                print("ERROR lABELS", line)

parenthesis_remover = re.compile('\(.*?\)')

babelnet_client = BabelNetClient('9ed6492f-0659-4d58-bd57-5ef4f7d16ce9')
for key, value in wikipedia_ids.iteritems():
    print "========== %s ==========" % value['food'].name.center(20)
    print "=> %s" % str(value['ingredient'].french_labels)
    lemmas = []
    for r in babelnet_client.get_synset_ids(value['food'].name, 'EN', filterLangs='EN', source='WIKT', pos='NOUN'):
        result = babelnet_client.get_synset(r['id'], filterLangs='FR')
        flag = result.get(u'domains', {}).get(u'FOOD_AND_DRINK') is not None
        for category in result.get(u'categories', []):
            if category[u'category'] in (u'Fruit', ) and category[u'language'] == u'EN':
                flag = True
        if flag:
            lemmas.extend([(sense[u'lemma'], sense[u'frequency']) for sense in result.get('senses', []) if sense[u'language']  == u'FR'])
    
    if len(lemmas) > 0:
        mean = sum(frequency for lemma, frequency in lemmas) / len(lemmas)
        for lemma, frequency in lemmas:
            if frequency >= mean:
                word = parenthesis_remover.sub('', lemma.replace('_', ' ')).strip()
                print(word, frequency)
                value['ingredient'].french_labels.append(word)

    value['ingredient'].french_labels = list(set(value['ingredient'].french_labels))
    print("save", value['ingredient'].french_labels)

    try:
        pg_session.add(value['ingredient'])
        pg_session.commit()
    except Exception, e:
        pg_session.rollback()
        print("ERROR", e)


pg_session.close()



