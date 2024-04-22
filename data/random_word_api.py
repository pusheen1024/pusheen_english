from flask import Blueprint, jsonify

from words_api import WordsAPI

blueprint = Blueprint('random_word_api', __name__, template_folder='templates')
words_api = WordsAPI()


@blueprint.route('/api/random_word')
def get_word():
    word = words_api.get_word()
    entry = words_api.get_entry(word)
    return jsonify({'word': word, 'entry': entry})
