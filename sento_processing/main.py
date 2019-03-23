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


import asyncio
import operator

import spacy

from sento_processing.database import (get_unprocessed_batch,
                                       store_processed_batch)
from sento_processing.logger import get_logger, get_queue_listener
from sento_processing.settings import get_config

_logger = get_logger()

_sentiment_categories = {
    'N': -1,
    'NEU': 0,
    'P': 1
}


async def main():
    _logger.info('Launching Sento Processing...')

    await run_processing_loop()


def _get_analysis_result(nlp, text):
    nlp_result = nlp(text)
    category = max(nlp_result.cats.items(), key=operator.itemgetter(1))[0]
    return _sentiment_categories.get(category)


async def run_processing_loop():
    config = get_config()

    _logger.info('Loading NLP model from path %s', config.SPACY_MODEL_PATH)
    nlp = spacy.load(config.SPACY_MODEL_PATH)
    _logger.info('Model successfully loaded')

    while True:
        _logger.info('Getting unprocessed batch')
        tweets = await get_unprocessed_batch()

        if tweets:
            _logger.info('Processing batch')
            processed_batch = [
                (t.get('id'), _get_analysis_result(nlp, t.get('content')))
                for t in tweets
            ]
            _logger.info('Batch successfully processed')

            _logger.info('Storing processed batch')
            await store_processed_batch(processed_batch)
            _logger.info('Batch successfully stored')
        else:
            _logger.info('No batches available, sleeping for 5 minutes')
            await asyncio.sleep(5*60)  # Sleep for 5 minutes


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        get_queue_listener().stop()
