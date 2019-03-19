# Copyright (C) 2019 Roberto García Calero (garcalrob@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Script for training the TextCategorizer component of a new spaCy model.

Based on the example available on
https://spacy.io/usage/training#section-textcat
"""


import random
from pathlib import Path

import plac
import spacy
from spacy.util import compounding, minibatch

from sento_processing.logger import get_logger, get_queue_listener
from sento_processing.readers import read_tass_dataset

_TASS_basepath = (Path().absolute().parent
                  .joinpath('resources', 'TASS-Datasets'))
_logger = get_logger()


@plac.annotations(
    model=('Model name. Defaults to blank "es" model.', 'option', 'm', str),
    output_dir=('Optional output directory', 'option', 'o', Path),
    n_iter=('Number of training iterations', 'option', 'n', int)
)
def main(model=None, output_dir=None, n_iter=20):
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()

    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        _logger.info('Loaded model "%s"', model)
    else:
        nlp = spacy.blank('es')  # create blank Language class
        _logger.info('Created blank "es" model')

    # add the text classifier to the pipeline if it doesn't exist
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'textcat' not in nlp.pipe_names:
        textcat = nlp.create_pipe('textcat')
        nlp.add_pipe(textcat, last=True)
    # otherwise, get it, so we can add labels to it
    else:
        textcat = nlp.get_pipe('textcat')

    # add labels to text classifier
    textcat.add_label('P')
    textcat.add_label('N')
    textcat.add_label('NEU')

    _logger.info('Loading TASS data')
    (train_texts, train_cats), (dev_texts, dev_cats) = load_data()
    _logger.info('Training samples: %d | Testing examples: %d',
                 len(train_texts), len(dev_texts))

    # Spacy model needs all the categories inside a dict with the 'cats' key
    train_data = list(zip(
        [_.content for _ in train_texts],
        [{'cats': _} for _ in train_cats]
    ))

    # Get all the model pipes that are not the category pipe
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'textcat']

    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()

        _logger.info('Training the model...')
        _logger.info('{:^5}\t{:^5}\t{:^5}\t{:^5}'
                     .format('LOSS', 'P', 'R', 'F'))

        for i in range(n_iter):
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.2,
                           losses=losses)

            with textcat.model.use_params(optimizer.averages):
                # evaluate on the dev data split off in load_data()
                scores = evaluate(nlp.tokenizer, textcat, [
                                  _.content for _ in dev_texts], dev_cats)

            _logger.info(
                '{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}'.format(
                    losses['textcat'],
                    scores['textcat_p'],
                    scores['textcat_r'],
                    scores['textcat_f']
                )
            )

    if output_dir is not None:
        with nlp.use_params(optimizer.averages):
            nlp.to_disk(output_dir)
        _logger.info('Saved model to %s', output_dir)


def load_data():
    train_filepath = _TASS_basepath.joinpath('general-train-tagged-3l.xml')
    test_filepath = _TASS_basepath.joinpath('general-test1k-tagged-3l.xml')

    _logger.info('Loading training data from %s', train_filepath)
    training_data = read_tass_dataset(train_filepath)

    _logger.info('Loading test/dev data from %s', test_filepath)
    dev_data = read_tass_dataset(test_filepath)

    random.shuffle(training_data)
    random.shuffle(dev_data)

    training_categories = [
        {
            'P': tweet.polarity_value == 'P',
            'N': tweet.polarity_value == 'N',
            'NEU': tweet.polarity_value == 'NEU'
        }
        for tweet in training_data
    ]

    dev_categories = [
        {
            'P': tweet.polarity_value == 'P',
            'N': tweet.polarity_value == 'N',
            'NEU': tweet.polarity_value == 'NEU'
        }
        for tweet in dev_data
    ]

    return ((training_data, training_categories),
            (dev_data, dev_categories))


def evaluate(tokenizer, textcat, texts, cats):
    docs = (tokenizer(text) for text in texts)
    tp = 0.0   # True positives
    fp = 1e-8  # False positives
    fn = 1e-8  # False negatives
    tn = 0.0   # True negatives
    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]
        for label, score in doc.cats.items():
            if label not in gold:
                continue
            if score >= 0.5 and gold[label] >= 0.5:
                tp += 1.0
            elif score >= 0.5 and gold[label] < 0.5:
                fp += 1.0
            elif score < 0.5 and gold[label] < 0.5:
                tn += 1
            elif score < 0.5 and gold[label] >= 0.5:
                fn += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if (precision+recall) == 0:
        f_score = 0.0
    else:
        f_score = 2 * (precision * recall) / (precision + recall)
    return {'textcat_p': precision, 'textcat_r': recall, 'textcat_f': f_score}


if __name__ == '__main__':
    try:
        plac.call(main)
    finally:
        get_queue_listener().stop()
