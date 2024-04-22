import json
import csv
import string

start_letter = {char: list() for char in string.ascii_lowercase}
with open('english-word-list-nouns.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for line in reader:
        word = line[1].strip()
        if len(word) > 1 and len(word.split()) == 1 and not word.istitle():
            start_letter[word[0]].append(word)
start_letter['x'].extend(['xenophobia', 'xenon', 'xylophone'])
start_letter['z'].extend(['zest', 'zealous', 'zoo', 'zebra'])
json.dump(start_letter, open('start_letter.json', 'w'))
