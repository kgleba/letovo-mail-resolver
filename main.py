import os
from operator import methodcaller

from flask import abort, Flask, request
from flask_cors import CORS

import db


def process_candidates(raw_names: str, raw_mails: str) -> dict[str, str]:
    mails = list(filter(bool, raw_mails[7:].split(';')))
    names = list(filter(bool, raw_names.split(';')))

    flattened_names = []
    for name in names:
        if ',' in name:
            flattened_names += list(map(methodcaller('strip'), name.split(',')))
        else:
            flattened_names.append(name)

    unique_names = list(dict.fromkeys(flattened_names))

    candidates = {name: mail for name, mail in zip(unique_names, mails)}
    return candidates


app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return ''


@app.route('/parse', methods=['POST'])
def process_data():
    names = request.json.get('names')
    mails = request.json.get('mails')

    if names is None or mails is None:
        abort(400)

    result = db.add_teachers(process_candidates(names, mails))

    if not result:
        return abort(500)

    return 'Successfully added teachers!'


@app.route('/search', methods=['POST'])
def search_data():
    name = request.json.get('name')
    if name is None:
        return abort(400)

    teacher = db.get_teacher_by_name(name)
    if teacher is None:
        return abort(404)

    return {'name': teacher['name'], 'mail': teacher['mail']}


if __name__ == '__main__':
    app.run('0.0.0.0', int(os.getenv('PORT', 80)))
