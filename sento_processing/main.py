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

# Based on the example available on
# https://spacy.io/usage/training#section-textcat

import random
from pathlib import Path

import plac
import spacy
from spacy.util import compounding, minibatch

from sento_processing.readers import read_tass_dataset

TASS_basepath = (Path().cwd().parent
                 .joinpath('resources', 'TASS-Datasets'))


@plac.annotations(
    model=('Model name. Defaults to blank "es" model.', 'option', 'm', str),
    output_dir=('Optional output directory', 'option', 'o', Path),
    n_texts=('Number of texts to train from', 'option', 't', int),
    n_iter=('Number of training iterations', 'option', 'n', int),
    use_gpu=('Use GPU', 'option', 'g', int)
)
def main(model=None, output_dir=None, n_iter=20, n_texts=2000, use_gpu=-1):
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()

    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('es')  # create blank Language class
        print("Created blank 'es' model")

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

    (train_texts, train_cats), (dev_texts, dev_cats) = load_data(limit=n_texts)


def load_data():
    training_data = read_tass_dataset(
        TASS_basepath.joinpath('general-train-tagged-3l.xml')
    )
    dev_data = read_tass_dataset(
        TASS_basepath.joinpath('general-test1k-tagged-3l.xml')
    )

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


if __name__ == '__main__':
    main()
