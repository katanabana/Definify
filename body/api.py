from requests import get
from keys import API_KEY


def get_json_response(url_end, additional_params=None):
    if additional_params is None:
        additional_params = {}
    url = 'http://api.wordnik.com/v4/' + url_end
    params = {
        'api_key': API_KEY
    }
    for additional_param in additional_params:
        params[additional_param] = additional_params[additional_param]
    try:
        return get(url, params=params).json()
    except Exception as ex:
        print('API ERROR')
        print(ex)
        print('url:', url, 'params:', params)


def get_random_word():
    try:
        params = {
            'minLength': 3,
            'maxLength': 10,
            'minCorpusCount': get_high_frequency() // 500

        }
        response = get_json_response('words.json/randomWord', params)
        return response['word']
    except Exception as ex:
        print('API ERROR')
        print(ex)


def get_high_frequency():
    try:
        word = 'the'  # one of the most frequently used words
        params = {'startYear': 2008}
        json = get_json_response(f'word.json/{word}/frequency', params)
        recent_frequencies = [freq['count'] for freq in json['frequency']]
        average = sum(recent_frequencies) / len(recent_frequencies)
        return round(average)
    except Exception as ex:
        print('API ERROR')
        print(ex)