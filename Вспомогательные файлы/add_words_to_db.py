import csv

from data import db_session
from data.words_model import Nouns, Verbs, Adjectives
from words_api import WordsAPI

words_api = WordsAPI()
db_session.global_init('db/english.db')
db_sess = db_session.create_session()
categories = {'nouns': Nouns, 'verbs': Verbs, 'adjectives': Adjectives}

for part_of_speech, class_name in categories.items():
    with open(f'data/english-word-list-{part_of_speech}.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for line in reader:
            word = line[1]
            try:
                entry = words_api.get_entry(word)
                transcription = entry['def'][0]['ts']
                synonyms = [syn['text'] for syn in entry['def'][0]['tr']]
                if not synonyms:
                    raise ValueError
                obj = class_name(word=word)
                db_sess.add(obj)
                db_sess.commit()
            except (ValueError, KeyError, IndexError):
                pass
