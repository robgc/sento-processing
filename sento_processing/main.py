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

import spacy

from sento_processing.database import (get_unprocessed_batch,
                                       store_processed_batch)
from sento_processing.logger import get_logger, get_queue_listener

_logger = get_logger()


async def main():
    _logger.info('Launching Sento Processing...')

    await run_processing_loop()


async def run_processing_loop():
    _logger.info('Loading NLP model')
    nlp = spacy.load()  # TODO: Make model path configurable

    _logger.info('Model successfully loaded')

    while True:
        _logger.info('Getting unprocessed batch')
        tweets = await get_unprocessed_batch()

        if tweets:
            _logger.info('Processing batch and storing it')
            store_processed_batch(
                [(t.get('id'), nlp(t.get('content'))) for t in tweets]
            )
            _logger.info('Batch successfully loaded')
        else:
            _logger.info('No batches available, sleeping for 5 minutes')
            asyncio.sleep(5*60)  # Sleep for 5 minutes


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        get_queue_listener().stop()
