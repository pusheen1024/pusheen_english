import json
import random
import itertools

import requests
from reverso_context_api import Client

from data import db_session
from data.words_model import Nouns, Verbs, Adjectives
from config import YANDEX_DICT


class WordsAPI:
    def __init__(self):
        self.dictionary_server = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'
        self.reverso_client = Client("en", "ru")
        db_session.global_init("db/english.db")
        self.session = db_session.create_session()
        self.categories = [Nouns, Verbs, Adjectives]

    def get_word(self):
        category = random.choice(self.categories)
        word = random.choice(self.session.query(category).all()).word
        return word

    def get_crossword_words(self, control_word):
        start_letter = json.load(open('data/start_letter.json'))
        words = dict()
        for letter in control_word:
            while True:
                try:
                    word = random.choice(start_letter[letter])
                    entry = self.get_entry(word)
                    synonyms = [syn['text'] for syn in entry['def'][0]['tr'] if word not in syn['text']]
                    chosen_synonyms = random.sample(synonyms, min(3, len(synonyms)))
                    if word not in words and chosen_synonyms:
                        words[word] = chosen_synonyms
                        break
                except Exception:
                    continue
        return words

    def get_entry(self, word):
        params = {'key': YANDEX_DICT,
                  'lang': 'en-en',
                  'text': word,
                  'format': 'json'}
        return requests.get(self.dictionary_server, params=params).json()

    def get_sentences(self, word):
        sentences = list()
        phrases = list(itertools.islice(self.reverso_client.get_translation_samples(word, cleanup=True), 3))
        for context in phrases:
            phrase = context[0].replace(word, ' '.join(['_'] * len(word)))
            sentences.append(phrase)
        return sentences
