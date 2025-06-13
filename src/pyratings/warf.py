# Copyright 2023 HSBC Global Asset Management (Deutschland) GmbH
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

"""Module holds functions to work with WARFs.

All functions use the following translation table.

| Moody’s |  S&P | Fitch | DBRS | Bloomberg | Score |  WARF | MinWARF* | MaxWARF* |
|:-------:|:----:|:-----:|:----:|:---------:|------:|------:|---------:|---------:|
|   Aaa   |  AAA |  AAA  |  AAA |    AAA    |     1 |     1 |        1 |        5 |
|   Aa1   |  AA+ |  AA+  |  AAH |    AA+    |     2 |    10 |        5 |       15 |
|   Aa2   |  AA  |   AA  |  AA  |     AA    |     3 |    20 |       15 |       30 |
|   Aa3   |  AA- |  AA-  |  AAL |    AA-    |     4 |    40 |       30 |       55 |
|    A1   |  A+  |   A+  |  AH  |     A+    |     5 |    70 |       55 |       95 |
|    A2   |   A  |   A   |   A  |     A     |     6 |   120 |       95 |      150 |
|    A3   |  A-  |   A-  |  AL  |     A-    |     7 |   180 |      150 |      220 |
|   Baa1  | BBB+ |  BBB+ | BBBH |    BBB+   |     8 |   260 |      220 |      310 |
|   Baa2  |  BBB |  BBB  |  BBB |    BBB    |     9 |   360 |      310 |      485 |
|   Baa3  | BBB- |  BBB- | BBBL |    BBB-   |    10 |   610 |      485 |      775 |
|   Ba1   |  BB+ |  BB+  |  BBH |    BB+    |    11 |   940 |      775 |     1145 |
|   Ba2   |  BB  |   BB  |  BB  |     BB    |    12 |  1350 |     1145 |     1558 |
|   Ba3   |  BB- |  BB-  |  BBL |    BB-    |    13 |  1766 |     1558 |     1993 |
|    B1   |  B+  |   B+  |  BH  |     B+    |    14 |  2220 |     1993 |     2470 |
|    B2   |   B  |   B   |   B  |     B     |    15 |  2720 |     2470 |     3105 |
|    B3   |  B-  |   B-  |  BL  |     B-    |    16 |  3490 |     3105 |     4130 |
|   Caa1  | CCC+ |  CCC+ | CCCH |    CCC+   |    17 |  4770 |     4130 |     5635 |
|   Caa2  |  CCC |  CCC  |  CCC |    CCC    |    18 |  6500 |     5635 |     7285 |
|   Caa3  | CCC- |  CCC- | CCCL |    CCC-   |    19 |  8070 |     7285 |     9034 |
|    Ca   |  CC  |   CC  |  CC  |     CC    |    20 |  9998 |     9034 |   9998.5 |
|    C    |   C  |   C   |   C  |     C     |    21 |  9999 |   9998.5 |   9999.5 |
|    D    |   D  |   D   |   D  |    DDD    |    22 | 10000 |   9999.5 |    10000 |

`MinWARF` is inclusive, while `MaxWARF` is exclusive.

"""

from __future__ import annotations  # required for Python < 3.10

import sqlite3

from pyratings.utils import RATINGS_DB


def get_warf_buffer(warf: float) -> float | int:
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
