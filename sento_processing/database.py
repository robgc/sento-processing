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


import asyncpg
from sento_processing.settings import get_config

_conn_pool = None  # type: asyncpg.pool.Pool


async def _get_conn_pool():
    global _conn_pool
    if _conn_pool is None:
        config = get_config()
        _conn_pool = await asyncpg.create_pool(
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWD,
            database=config.POSTGRES_DB_NAME
        )
    return _conn_pool


async def get_unprocessed_batch(batch_size=100):
    results = None  # type: asyncpg.Record
    async with _get_conn_pool() as conn:
        results = await conn.fetch(
            """
            SELECT
              s.id AS id,
              s.content AS content
            FROM
              data.statuses
            WHERE
              sentiment IS NULL
            LIMIT $1
            """,
            batch_size
        )
    return results


async def store_processed_batch(batch):
    async with _get_conn_pool() as conn:
        async with conn.transaction():
            await conn.executemany(
                """
                UPDATE
                  data.statuses
                SET
                  sentiment = $2
                WHERE
                  id = $1
                """,
                batch
            )
