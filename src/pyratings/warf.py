# Copyright 2022 HSBC Global Asset Management (Deutschland) GmbH
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Module holds functions to work with WARFs."""

import sqlite3
from typing import Union

from pyratings.utils import RATINGS_DB


def get_warf_buffer(warf: Union[float, int]) -> Union[float, int]:
    """Compute WARF buffer.

    The WARF buffer is the distance from current WARF to the next maxWARF level. It
    determines the room until a further rating downgrade.

    Parameters
    ----------
    warf
        Numerical WARF.

    Returns
    -------
    Union[float, int]
        WARF buffer.

    Examples
    --------
    >>> get_warf_buffer(warf=480)
    5.0

    >>> get_warf_buffer(warf=54)
    1.0
    """
    # connect to database
    connection = sqlite3.connect(RATINGS_DB)
    cursor = connection.cursor()

    # create SQL query
    sql_query = "SELECT MaxWARF FROM WARFs WHERE ? >= MinWARF and ? < MaxWARF"

    # execute SQL query
    cursor.execute(sql_query, (warf, warf))
    max_warf = cursor.fetchall()

    # close database connection
    connection.close()

    return max_warf[0][0] - warf
