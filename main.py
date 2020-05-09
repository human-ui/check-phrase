import difflib

from flask import Flask, render_template, request
from transformers import AutoModelWithLMHead, AutoTokenizer, pipeline


app = Flask(__name__)

model_name = 'roberta-large'
model = AutoModelWithLMHead.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
MASK = '_'

fill_mask = pipeline('fill-mask', model=model, tokenizer=tokenizer)


def gen(inp):
    inp = inp.strip()

    if MASK not in inp:
        raise ValueError(f'ERROR: Please include {MASK} in your input.')
    if len(inp.split(MASK)) > 2:
        raise ValueError(f'ERROR: Please include only a single {MASK} in your input.')

    output = fill_mask(inp.replace(MASK, '<mask>'))

    clean_output = []
    for item in output:
        pred = item['sequence'].replace('<s> ', '').replace('</s>', '').strip()
        diff = difflib.ndiff(inp, pred)
        fill_in = ''.join([w[2:] for w in diff if w.startswith('+')])
        clean_output.append((fill_in, item['score']))
    return clean_output


def _get_most_likely(scores):
    scores_sorted = sorted(scores, key=scores.get, reverse=True)
    return scores_sorted[0]


def _format_scores(scores):
    return [f'{w}: {s:.2f}' for w, s in scores.items()]


def fill_in_article(outputs):
    scores = {'no article': 0, 'a': 0, 'an': 0, 'the': 0}
    # articles = {'a': 'a', 'the': 'the', 'no article': ''}

    for word, score in outputs:
        if word.lower() not in ['a', 'an', 'the']:
            key = 'no article'
        else:
            key = word.lower()

        scores[key] += score

    most_likely = _get_most_likely(scores)
    if most_likely == 'no article':
        most_likely = ''

    # remove either a or an or show a(n) instead
    if scores['a'] == 0 and scores['an'] == 0:
        scores['a(n)'] = 0
        del scores['a']
        del scores['an']
    elif scores['an'] == 0:
        del scores['an']
    elif scores['a'] == 0:
        del scores['a']

    return most_likely, scores


def fill_in_any_word(outputs):
    scores = {w: s for w, s in outputs}
    most_likely = _get_most_likely(scores)
    return most_likely, scores


@app.route('/', methods=['GET', 'POST'])
def root():
    inp = 'Lucy in _ sky with diamonds.'

    OPTIONS = {
        'article': fill_in_article,
        'any_word': fill_in_any_word
    }
    checked = {'article': 'checked', 'any_word': ''}
    sentence = {}
    scores = []
    if request.method == 'POST':
        inp = request.form.get('inp')
        if inp is not None:
            outputs = gen(inp)
            option = request.form.get('options', 'article')
            checked = {k: 'checked' if k == option else '' for k in checked}
            process = OPTIONS[option]
            most_likely, scores = process(outputs)
            scores = _format_scores(scores)
            start, end = inp.split(MASK)
            sentence = {'part1': start.strip(),
                        'fill_in': most_likely,
                        'part2': end.strip()}

    return render_template('index.html', inp=inp, scores=scores,
                           checked=checked, **sentence)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
