import random
import json

from words_api import WordsAPI

words_api = WordsAPI()

with open('data/start_letter.json') as json_file:
    start_letter = json.load(json_file)
    filtered_start_letter = {key: list() for key in start_letter}
    for key in start_letter:
        for word in start_letter[key]:
            entry = words_api.get_entry(word)
            try:
                definitions = list(map(lambda x: x['text'], entry['def'][0]['tr']))
                if len(definitions) >= 2:
                    definitions = random.sample(definitions, 2)
                filtered_start_letter[key].append({word: definitions})
            except (IndexError, KeyError):
                pass
    json.dump(filtered_start_letter, open('data/start_letter.json', 'w'))
