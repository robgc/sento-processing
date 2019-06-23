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


from configparser import ConfigParser
from pathlib import Path

_config = None  # type: Config


class Config:
    def __init__(self):
        parser = ConfigParser()
        config_path = (
            Path(__file__)
            .absolute()
            .parents[1]
            .joinpath('config.ini')
        )
        parser.read(config_path)

        # Config file
        # Logging
        logging_section = parser['logging']
        self.LOGGING_LEVEL = logging_section.get('level')
        self.LOGGING_OUTPUT = logging_section.get('output')

        # Postgres
        pg_section = parser['postgres']
        self.POSTGRES_HOST = pg_section.get('host', 'postgres')
        self.POSTGRES_PORT = int(pg_section.get('port', 5432))
        self.POSTGRES_USER = pg_section.get('user')
        self.POSTGRES_DB_NAME = pg_section.get('db_name', 'sento')
        self.POSTGRES_PASSWD = pg_section.get('password', 'sento')

        # NLP
        model_path = Path(parser['nlp'].get('model_path'))
        if not model_path.is_absolute():
            model_path = config_path.parent.joinpath(model_path)

        self.SPACY_MODEL_PATH = model_path


def get_config():
    global _config
    if _config is None:
        _config = Config()
    return _config
