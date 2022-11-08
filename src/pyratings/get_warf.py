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

"""Module contains functions to translate ratings / rating scores into WARF(s).

All functions use the following table in order to translate between long-term
ratings/numerical scores and WARF.

| Moody’s |  S&P | Fitch |  ICE | DBRS | Bloomberg | Score |  WARF |
|:-------:|:----:|:-----:|:----:|:----:|:---------:|------:|------:|
|   Aaa   |  AAA |  AAA  |  AAA |  AAA |    AAA    |     1 |     1 |
|   Aa1   |  AA+ |  AA+  |  AA+ |  AAH |    AA+    |     2 |    10 |
|   Aa2   |  AA  |   AA  |  AA  |  AA  |     AA    |     3 |    20 |
|   Aa3   |  AA- |  AA-  |  AA- |  AAL |    AA-    |     4 |    40 |
|    A1   |  A+  |   A+  |  A+  |  AH  |     A+    |     5 |    70 |
|    A2   |   A  |   A   |   A  |   A  |     A     |     6 |   120 |
|    A3   |  A-  |   A-  |  A-  |  AL  |     A-    |     7 |   180 |
|   Baa1  | BBB+ |  BBB+ | BBB+ | BBBH |    BBB+   |     8 |   260 |
|   Baa2  |  BBB |  BBB  |  BBB |  BBB |    BBB    |     9 |   360 |
|   Baa3  | BBB- |  BBB- | BBB- | BBBL |    BBB-   |    10 |   610 |
|   Ba1   |  BB+ |  BB+  |  BB+ |  BBH |    BB+    |    11 |   940 |
|   Ba2   |  BB  |   BB  |  BB  |  BB  |     BB    |    12 |  1350 |
|   Ba3   |  BB- |  BB-  |  BB- |  BBL |    BB-    |    13 |  1766 |
|    B1   |  B+  |   B+  |  B+  |  BH  |     B+    |    14 |  2220 |
|    B2   |   B  |   B   |   B  |   B  |     B     |    15 |  2720 |
|    B3   |  B-  |   B-  |  B-  |  BL  |     B-    |    16 |  3490 |
|   Caa1  | CCC+ |  CCC+ | CCC+ | CCCH |    CCC+   |    17 |  4770 |
|   Caa2  |  CCC |  CCC  |  CCC |  CCC |    CCC    |    18 |  6500 |
|   Caa3  | CCC- |  CCC- | CCC- | CCCL |    CCC-   |    19 |  8070 |
|    Ca   |  CC  |   CC  |  CC  |  CC  |     CC    |    20 |  9998 |
|    C    |   C  |   C   |   C  |   C  |     C     |    21 |  9999 |
|    D    |   D  |   D   |   D  |   D  |    DDD    |    22 | 10000 |

"""

from typing import List, Optional, Union

import numpy as np
import pandas as pd

from pyratings.get_scores import get_scores_from_ratings
from pyratings.utils import (
    _extract_rating_provider,
    _get_translation_dict,
    valid_rtg_agncy,
)


def get_warf_from_scores(
    rating_scores: Union[int, float, pd.Series, pd.DataFrame],
) -> Union[int, pd.Series, pd.DataFrame]:
    """Convert numerical rating score(s) to numerical WARF(s).

    Parameters
    ----------
    rating_scores
        Numerical rating score(s).

    Returns
    -------
    Union[int, pd.Series, pd.DataFrame
        Numerical WARF(s).

        If returns a ``pd.Series``, the series name will be `warf` suffixed by
        `rating_scores.name`.

        If return a ``pd.DataFrame``, the column names will be `warf` suffixed
        by the respective `rating_scores.columns`.

    Examples
    --------
    Converting a single rating score:

    >>> get_warf_from_scores(10)
    610

    Converting a ``pd.Series`` with rating scores:

    >>> import pandas as pd
    >>> rating_scores_series = pd.Series(data=[5, 7, 1, np.nan, 22, pd.NA])
    >>> get_warf_from_scores(rating_scores=rating_scores_series)
    0       70.0
    1      180.0
    2        1.0
    3        NaN
    4    10000.0
    5        NaN
    Name: warf, dtype: float64

    Converting a ``pd.DataFrame`` with rating scores:

    >>> rating_scores_df = pd.DataFrame(
    ...     data=[[11, 16, "foo"], [4, 2, 1], [22, "bar", 22]],
    ...     columns=["provider1", "provider2", "provider3"],
    ... )
    >>> get_warf_from_scores(rating_scores=rating_scores_df)
       warf_provider1  warf_provider2  warf_provider3
    0             940          3490.0             NaN
    1              40            10.0             1.0
    2           10000             NaN         10000.0

    """
    warf_dict = _get_translation_dict("scores_to_warf")

    if isinstance(rating_scores, (int, float, np.number)):
        return warf_dict.get(rating_scores, np.nan)
    elif isinstance(rating_scores, pd.Series):
        warf = pd.Series(data=rating_scores.map(warf_dict))
        if rating_scores.name is not None:
            warf.name = "warf_" + str(rating_scores.name)
        else:
            warf.name = "warf"
        return warf
    elif isinstance(rating_scores, pd.DataFrame):
        return rating_scores.apply(lambda x: x.map(warf_dict)).add_prefix("warf_")


def get_warf_from_ratings(
    ratings: Union[str, pd.Series, pd.DataFrame],
    rating_provider: Optional[Union[str, List[str]]] = None,
) -> Union[int, pd.Series, pd.DataFrame]:
    """Convert regular rating(s) to numerical WARF(s).

    Parameters
    ----------
    ratings
        Regular rating(s) to be translated into WARF(s).
    rating_provider
        Should contain any valid rating provider out of {"Fitch", "Moody's", "S&P",
        "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider` will be inferred from the series name or dataframe
        column names.

    Returns
    -------
    Union[int, pd.Series, pd.DataFrame]
        Numerical WARF.

         If returns a ``pd.Series``, the series name will be `warf` suffixed by
        `ratings.name`.

        If return a ``pd.DataFrame``, the column names will be `warf` suffixed
        by the respective `ratings.columns`.

    Examples
    --------
    Converting a single rating:

    >>> get_warf_from_ratings(ratings="BB-", rating_provider="Fitch")
    1766

    Converting a ``pd.Series`` with ratings:

    >>> import numpy as np
    >>> import pandas as pd
    >>> ratings_series = pd.Series(data=["A1", "A3", "Aaa", np.nan, "D", pd.NA])
    >>> get_warf_from_ratings(
    ...     ratings=ratings_series, rating_provider="Moody's"
    ... )
    0       70.0
    1      180.0
    2        1.0
    3        NaN
    4    10000.0
    5        NaN
    Name: warf, dtype: float64

    Providing a ``pd.Series`` without specifying a `rating_provider`:

    >>> ratings_series = pd.Series(
    ...     data=["A1", "A3", "Aaa", np.nan, "D", pd.NA],
    ...     name="Moody's"
    ... )
    >>> get_warf_from_ratings(ratings=ratings_series)
    0       70.0
    1      180.0
    2        1.0
    3        NaN
    4    10000.0
    5        NaN
    Name: warf_Moody's, dtype: float64

    Converting a ``pd.DataFrame`` with ratings:

    >>> ratings_df = pd.DataFrame(
    ...     data=[["BB+", "B-", "foo"], ["AA-", "AA+", "AAA"], ["D", "bar", "C"]],
    ...     columns=["Fitch", "Bloomberg", "DBRS"],
    ... )
    >>> get_warf_from_ratings(
    ...     ratings= ratings_df, rating_provider=["Fitch", "Bloomberg", "DBRS"]
    ... )
       warf_Fitch  warf_Bloomberg  warf_DBRS
    0         940          3490.0        NaN
    1          40            10.0        1.0
    2       10000             NaN     9999.0

    When providing a ``pd.DataFrame`` without explicitly providing the
    `rating_provider`, they will be inferred by the dataframe's columns.

    >>> ratings_df = pd.DataFrame(
    ...     data={
    ...         "rtg_fitch": ["BB+", "AA-", "D"],
    ...         "rtg_Bloomberg": ["B-", "AA+", "bar"],
    ...         "DBRS Ratings": ["foo", "AAA", "C"]
    ...     }
    ... )
    >>> get_warf_from_ratings(ratings=ratings_df)
       warf_rtg_fitch  warf_rtg_Bloomberg  warf_DBRS Ratings
    0             940              3490.0                NaN
    1              40                10.0                1.0
    2           10000                 NaN             9999.0


    """
    if rating_provider is not None:
        rating_provider = _extract_rating_provider(
            rating_provider=rating_provider,
            valid_rtg_provider=valid_rtg_agncy["long-term"],
        )

    warf_dict = _get_translation_dict("scores_to_warf")
    if isinstance(ratings, str):
        rating_scores = get_scores_from_ratings(
            ratings=ratings, rating_provider=rating_provider, tenor="long-term"
        )
        return warf_dict.get(rating_scores, np.nan)

    elif isinstance(ratings, (pd.Series, pd.DataFrame)):
        rating_scores = get_scores_from_ratings(
            ratings=ratings, rating_provider=rating_provider, tenor="long-term"
        )
        if isinstance(ratings, pd.Series):
            rating_scores.name = ratings.name
        elif isinstance(ratings, pd.DataFrame):
            rating_scores.columns = ratings.columns
        return get_warf_from_scores(rating_scores=rating_scores)
