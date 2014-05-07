from unidecode import unidecode
import random
import requests


def password_suggestion(number_of_words):
    ''' generates a password suggestion from random wikipedia articles '''
    r = requests.get(
        "https://de.wikipedia.org/w/api.php?format=json&action=query&list=random&rnlimit=%i&rnnamespace=0" %
        (number_of_words * 5))
    words = []
    for item in r.json()['query']['random']:
        for title in item['title'].split():
            title = ''.join(e for e in unidecode(title) if e.isalnum())
            words.append(title)
    password = []
    while len(password) is not number_of_words:
        random_word = random.choice(words)
        if random_word not in password:
            password.append(random_word)
    return ' '.join(password)
