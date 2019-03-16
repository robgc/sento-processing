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


from collections import namedtuple
from xml.etree import ElementTree
import re

_TASSTweet = namedtuple('TASSTweet', ['content', 'polarity_value'])

_link_re = re.compile(r'https?:\/\/.*[\r\n]*')


def read_tass_dataset(file_path):
    tree = ElementTree.parse(file_path)
    root = tree.getroot()
    read_results = list()

    for tweet in root:
        # A tweet may have polarities applied to entities in the text
        # Extract only the "global" polarity, which is the first entry
        # inside the sentiments tag
        polarity = tweet.find('sentiments/polarity')
        content = (_link_re.sub('', tweet.find("content").text)
                   if tweet.find('content') is not None
                   and tweet.find('content').text is not None
                   else None)
        polarity_value = (polarity.find("value").text
                          if polarity.find("value") is not None
                          else None)

        if polarity_value is not None and polarity_value != 'NONE':
            read_results.push(_TASSTweet(content, polarity_value))

    return read_results
