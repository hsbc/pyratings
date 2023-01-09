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

"""Module contains functions to translate ratings / WARF into rating scores.

All functions use the following table in order to translate between long-term
ratings/WARF and numerical rating scores.

| Moody |  S&P | Fitch | DBRS | Bloomberg | Score |  WARF | MinWARF* | MaxWARF* |
|:-----:|:----:|:-----:|:----:|:---------:|------:|------:|---------:|---------:|
|  Aaa  |  AAA |  AAA  |  AAA |    AAA    |     1 |     1 |        1 |        5 |
|  Aa1  |  AA+ |  AA+  |  AAH |    AA+    |     2 |    10 |        5 |       15 |
|  Aa2  |  AA  |   AA  |  AA  |     AA    |     3 |    20 |       15 |       30 |
|  Aa3  |  AA- |  AA-  |  AAL |    AA-    |     4 |    40 |       30 |       55 |
|   A1  |  A+  |   A+  |  AH  |     A+    |     5 |    70 |       55 |       95 |
|   A2  |   A  |   A   |   A  |     A     |     6 |   120 |       95 |      150 |
|   A3  |  A-  |   A-  |  AL  |     A-    |     7 |   180 |      150 |      220 |
|  Baa1 | BBB+ |  BBB+ | BBBH |    BBB+   |     8 |   260 |      220 |      310 |
|  Baa2 |  BBB |  BBB  |  BBB |    BBB    |     9 |   360 |      310 |      485 |
|  Baa3 | BBB- |  BBB- | BBBL |    BBB-   |    10 |   610 |      485 |      775 |
|  Ba1  |  BB+ |  BB+  |  BBH |    BB+    |    11 |   940 |      775 |     1145 |
|  Ba2  |  BB  |   BB  |  BB  |     BB    |    12 |  1350 |     1145 |     1558 |
|  Ba3  |  BB- |  BB-  |  BBL |    BB-    |    13 |  1766 |     1558 |     1993 |
|   B1  |  B+  |   B+  |  BH  |     B+    |    14 |  2220 |     1993 |     2470 |
|   B2  |   B  |   B   |   B  |     B     |    15 |  2720 |     2470 |     3105 |
|   B3  |  B-  |   B-  |  BL  |     B-    |    16 |  3490 |     3105 |     4130 |
|  Caa1 | CCC+ |  CCC+ | CCCH |    CCC+   |    17 |  4770 |     4130 |     5635 |
|  Caa2 |  CCC |  CCC  |  CCC |    CCC    |    18 |  6500 |     5635 |     7285 |
|  Caa3 | CCC- |  CCC- | CCCL |    CCC-   |    19 |  8070 |     7285 |     9034 |
|   Ca  |  CC  |   CC  |  CC  |     CC    |    20 |  9998 |     9034 |   9998.5 |
|   C   |   C  |   C   |   C  |     C     |    21 |  9999 |   9998.5 |   9999.5 |
|   D   |   D  |   D   |   D  |    DDD    |    22 | 10000 |   9999.5 |    10000 |

`MinWARF` is inclusive, while `MaxWARF` is exclusive.

For short-term ratings, the rating will be translated into an equivalent long-term
rating score. The translation will depend on a "translation strategy". The following
translation table will be used:

|  Agency | Strategy |    Rating   | MinLTScore | MaxLTScore | AvgLTScore |
|:-------:|:--------:|:-----------:|:----------:|:----------:|:----------:|
| Moody's |   best   |     P-1     |      1     |      7     |    4.00    |
| Moody's |   best   |     P-2     |      8     |      9     |    8.50    |
| Moody's |   best   |     P-3     |     10     |     10     |   10.00    |
| Moody's |   best   |      NP     |     11     |     22     |   16.50    |
| Moody's |   base   |     P-1     |      1     |      6     |    3.50    |
| Moody's |   base   |     P-2     |      7     |      8     |    7.50    |
| Moody's |   base   |     P-3     |      9     |     10     |    9.50    |
| Moody's |   base   |      NP     |     11     |     22     |   16.50    |
| Moody's |   worst  |     P-1     |      1     |      5     |    3.00    |
| Moody's |   worst  |     P-2     |      6     |      8     |    7.00    |
| Moody's |   worst  |     P-3     |      9     |     10     |    9.50    |
| Moody's |   worst  |      NP     |     11     |     22     |   16.50    |
| S&P     |   best   |     A-1+    |      1     |      5     |    3.00    |
| S&P     |   best   |     A-1     |      6     |      7     |    6.50    |
| S&P     |   best   |     A-2     |      8     |      9     |    8.50    |
| S&P     |   best   |     A-3     |     10     |     11     |   10.50    |
| S&P     |   best   |      B      |     12     |     16     |   14.00    |
| S&P     |   best   |      C      |     17     |     21     |   19.00    |
| S&P     |   best   |      D      |     22     |     22     |   22.00    |
| S&P     |   base   |     A-1+    |      1     |      4     |    2.50    |
| S&P     |   base   |     A-1     |      5     |      6     |    5.50    |
| S&P     |   base   |     A-2     |      7     |      9     |    8.00    |
| S&P     |   base   |     A-3     |     10     |     10     |   10.00    |
| S&P     |   base   |      B      |     11     |     16     |   13.50    |
| S&P     |   base   |      C      |     17     |     21     |   19.00    |
| S&P     |   base   |      D      |     22     |     22     |   22.00    |
| S&P     |   worst  |     A-1+    |      1     |      4     |    2.50    |
| S&P     |   worst  |     A-1     |      5     |      6     |    5.50    |
| S&P     |   worst  |     A-2     |      7     |      9     |    8.00    |
| S&P     |   worst  |     A-3     |     10     |     10     |   10.00    |
| S&P     |   worst  |      B      |     11     |     16     |   13.50    |
| S&P     |   worst  |      C      |     17     |     21     |   19.00    |
| S&P     |   worst  |      D      |     22     |     22     |   22.00    |
| Fitch   |   best   |     F1+     |      1     |      6     |    3.50    |
| Fitch   |   best   |      F1     |      7     |      8     |    7.50    |
| Fitch   |   best   |      F2     |      9     |      9     |    9.00    |
| Fitch   |   best   |      F3     |     10     |     10     |   10.00    |
| Fitch   |   best   |      B      |     11     |     16     |   13.50    |
| Fitch   |   best   |      C      |     17     |     20     |   18.50    |
| Fitch   |   best   |      D      |     21     |     22     |   21.50    |
| Fitch   |   base   |     F1+     |      1     |      5     |    3.00    |
| Fitch   |   base   |      F1     |      6     |      7     |    6.50    |
| Fitch   |   base   |      F2     |      8     |      8     |    8.00    |
| Fitch   |   base   |      F3     |      9     |     10     |    9.50    |
| Fitch   |   base   |      B      |     11     |     16     |   13.50    |
| Fitch   |   base   |      C      |     17     |     20     |   18.50    |
| Fitch   |   base   |      D      |     21     |     22     |   21.50    |
| Fitch   |   worst  |     F1+     |      1     |      4     |    2.50    |
| Fitch   |   worst  |      F1     |      5     |      6     |    5.50    |
| Fitch   |   worst  |      F2     |      7     |      8     |    7.50    |
| Fitch   |   worst  |      F3     |      9     |     10     |    9.50    |
| Fitch   |   worst  |      B      |     11     |     16     |   13.50    |
| Fitch   |   worst  |      C      |     17     |     20     |   18.50    |
| Fitch   |   worst  |      D      |     21     |     22     |   21.50    |
| DBRS    |   best   |    R-1 H    |      1     |      3     |    2.00    |
| DBRS    |   best   |    R-1 M    |      4     |      5     |    4.50    |
| DBRS    |   best   |    R-1 L    |      6     |      8     |    7.00    |
| DBRS    |   best   |    R-2 H    |      9     |      9     |    9.00    |
| DBRS    |   best   |    R-2 M    |     10     |     10     |   10.00    |
| DBRS    |   best   |     R-3     |     11     |     11     |   11.00    |
| DBRS    |   best   |     R-4     |     12     |     15     |   13.50    |
| DBRS    |   best   |     R-5     |     16     |     21     |   18.50    |
| DBRS    |   best   |      D      |     22     |     22     |   22.00    |
| DBRS    |   base   |    R-1 H    |      1     |      2     |    1.50    |
| DBRS    |   base   |    R-1 M    |      3     |      4     |    3.50    |
| DBRS    |   base   |    R-1 L    |      5     |      7     |    6.00    |
| DBRS    |   base   |    R-2 H    |      8     |      8     |    8.00    |
| DBRS    |   base   |    R-2 M    |      9     |      9     |    9.00    |
| DBRS    |   base   | R-2 L / R-3 |     10     |     10     |   10.00    |
| DBRS    |   base   |     R-4     |     11     |     14     |   12.50    |
| DBRS    |   base   |     R-5     |     15     |     21     |   18.00    |
| DBRS    |   base   |      D      |     22     |     22     |   22.00    |
| DBRS    |   worst  |    R-1 H    |      1     |      1     |    1.00    |
| DBRS    |   worst  |    R-1 M    |      2     |      3     |    2.50    |
| DBRS    |   worst  |    R-1 L    |      4     |      6     |    5.00    |
| DBRS    |   worst  |    R-2 H    |      7     |      8     |    7.50    |
| DBRS    |   worst  |    R-2 M    |      9     |      9     |    9.00    |
| DBRS    |   worst  |     R-3     |     10     |     10     |   10.00    |
| DBRS    |   worst  |     R-4     |     11     |     14     |   12.50    |
| DBRS    |   worst  |     R-5     |     15     |     21     |   18.00    |
| DBRS    |   worst  |      D      |     22     |     22     |   22.00    |

"""

import sqlite3
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from pyratings.utils import (
    RATINGS_DB,
    VALUE_ERROR_PROVIDER_MANDATORY,
    _extract_rating_provider,
    _get_translation_dict,
    valid_rtg_agncy,
)


def get_scores_from_ratings(
    ratings: Union[str, pd.Series, pd.DataFrame],
    rating_provider: Optional[Union[str, List[str]]] = None,
    tenor: str = "long-term",
) -> Union[int, pd.Series, pd.DataFrame]:
    """Convert regular ratings into numerical rating scores.

    Parameters
    ----------
    ratings
        Rating(s) to be translated into rating score(s).
    rating_provider
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.

        If None, `rating_provider` will be inferred from the series name or dataframe
        column names.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    Union[int, pd.Series, pd.DataFrame]
        Numerical rating score(s)

        If returns a ``pd.Series``, the series name will be `rtg_score`
        suffixed by `ratings.name`.

        If return a ``pd.DataFrame``, the column names will be `rtg_score` suffixed
        by the respective `ratings.columns`.

    Raises
    ------
    ValueError
        If providing a single rating and `rating_provider` is None.

    Examples
    --------
    Converting a single long-term rating:

    >>> get_scores_from_ratings(
    ...     ratings="BBB-", rating_provider="S&P", tenor="long-term"
    ... )
    10

    Converting a single short-term rating score:

    >>> get_scores_from_ratings(
    ...     ratings="P-1", rating_provider="Moody", tenor="short-term"
    ... )
    3.5

    Converting a ``pd.Series`` of ratings:

    >>> import pandas as pd
    >>> ratings_series = pd.Series(
    ...     data=["Baa1", "C", "NR", "WD", "D", "B1", "SD"], name='Moody'
    ... )
    >>> get_scores_from_ratings(
    ...     ratings=ratings_series, rating_provider="Moody's", tenor="long-term"
    ... )
    0     8.0
    1    21.0
    2     NaN
    3     NaN
    4    22.0
    5    14.0
    6    22.0
    Name: rtg_score_Moody, dtype: float64

    Providing a ``pd.Series`` without specifying a `rating_provider`:

    >>> ratings_series = pd.Series(
    ...     data=["Baa1", "C", "NR", "WD", "D", "B1", "SD"], name="Moody"
    ... )
    >>> get_scores_from_ratings(ratings=ratings_series)
    0     8.0
    1    21.0
    2     NaN
    3     NaN
    4    22.0
    5    14.0
    6    22.0
    Name: rtg_score_Moody, dtype: float64

    Converting a ``pd.DataFrame`` with ratings:

    >>> ratings_df = pd.DataFrame(
    ...     data=[["BB+", "B3", "BBB-"], ["AA-", "Aa1", "AAA"], ["D", "NR", "D"]],
    ...     columns=["SP", "Moody", "DBRS"],
    ... )
    >>> get_scores_from_ratings(
    ...     ratings=ratings_df,
    ...     rating_provider=["S&P", "Moody's", "DBRS"],
    ...     tenor="long-term",
    ... )
       rtg_score_SP  rtg_score_Moody  rtg_score_DBRS
    0            11             16.0             NaN
    1             4              2.0             1.0
    2            22              NaN            22.0

    When providing a ``pd.DataFrame`` without explicitly providing the
    `rating_provider`, they will be inferred from the dataframe's columns.

    >>> ratings_df = pd.DataFrame(
    ...     data={
    ...         "rtg_fitch": ["BB+", "AA-", "D"],
    ...         "rtg_Bloomberg": ["B-", "AA+", "NR"],
    ...         "DBRS Ratings": ["BBB-", "AAA", "D"],
    ...     }
    ... )
    >>> get_scores_from_ratings(ratings=ratings_df)
       rtg_score_rtg_fitch  rtg_score_rtg_Bloomberg  rtg_score_DBRS Ratings
    0                   11                     16.0                     NaN
    1                    4                      2.0                     1.0
    2                   22                      NaN                    22.0

    """
    if isinstance(ratings, str):
        if rating_provider is None:
            raise ValueError(VALUE_ERROR_PROVIDER_MANDATORY)

        rating_provider = _extract_rating_provider(
            rating_provider=rating_provider,
            valid_rtg_provider=valid_rtg_agncy[tenor],
        )

        rtg_dict = _get_translation_dict(
            "rtg_to_scores",
            rating_provider,
            tenor=tenor,
            st_rtg_strategy="base",
        )
        return rtg_dict.get(ratings, pd.NA)

    elif isinstance(ratings, pd.Series):
        if rating_provider is None:
            rating_provider = _extract_rating_provider(
                rating_provider=ratings.name,
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider,
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )

        rtg_dict = _get_translation_dict(
            "rtg_to_scores",
            rating_provider,
            tenor=tenor,
            st_rtg_strategy="base",
        )
        return pd.Series(data=ratings.map(rtg_dict), name=f"rtg_score_{ratings.name}")

    elif isinstance(ratings, pd.DataFrame):
        if rating_provider is None:
            rating_provider = _extract_rating_provider(
                rating_provider=ratings.columns.to_list(),
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider,
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )

        # Recursive call of `get_scores_from_ratings`
        return pd.concat(
            [
                get_scores_from_ratings(
                    ratings=ratings[col],
                    rating_provider=provider,
                    tenor=tenor,
                )
                for col, provider in zip(ratings.columns, rating_provider)
            ],
            axis=1,
        )


def get_scores_from_warf(
    warf: Union[int, float, pd.Series, pd.DataFrame]
) -> Union[int, float, pd.Series, pd.DataFrame]:
    """Convert weighted average rating factors (WARFs) into numerical rating scores.

    Parameters
    ----------
    warf
        Weighted average rating factor (WARF).

    Returns
    -------
    Union[int, float, pd.Series, pd.DataFrame]
        Numerical rating score(s).

    Examples
    --------
    Converting a single WARF:

    >>> get_scores_from_warf(500)
    10

    >>> get_scores_from_warf(1992.9999)
    13

    Converting a ``pd.Series`` of WARFs:

    >>> import numpy as np
    >>> import pandas as pd
    >>> warf_series = pd.Series(data=[260, 9999.49, np.nan, 10000, 2469.99, 2470])
    >>> get_scores_from_warf(warf=warf_series)
    0     8.0
    1    21.0
    2     NaN
    3    22.0
    4    14.0
    5    15.0
    Name: rtg_score, dtype: float64

    Converting a ``pd.DataFrame`` of WARFs:

    >>> warf_df = pd.DataFrame(
    ...     data={
    ...         "provider1": [900, 40, 10000],
    ...         "provider2": [3000, 10, np.nan],
    ...         "provider3": [610, 1, 9999.49],
    ...     }
    ... )
    >>> get_scores_from_warf(warf=warf_df)
       rtg_score_provider1  rtg_score_provider2  rtg_score_provider3
    0                   11                 15.0                   10
    1                    4                  2.0                    1
    2                   22                  NaN                   21

    """

    def _get_scores_from_warf_db(
        wrf: Union[int, float, pd.Series, pd.DataFrame]
    ) -> Union[int, float]:
        if not isinstance(wrf, (int, float, np.number) or np.isnan(wrf)) or not (
            1 <= wrf <= 10_000
        ):
            return np.nan
        else:
            if wrf == 10_000:
                return 22

            else:
                # connect to database
                connection = sqlite3.connect(RATINGS_DB)
                cursor = connection.cursor()

                # create SQL query
                sql_query = (
                    "SELECT RatingScore FROM WARFs WHERE ? >= MinWARF and ? < MaxWARF"
                )

                # execute SQL query
                cursor.execute(sql_query, (wrf, wrf))
                rtg_score = cursor.fetchall()

                # close database connection
                connection.close()

                return rtg_score[0][0]

    if isinstance(warf, (int, float, np.number)):
        return _get_scores_from_warf_db(warf)

    elif isinstance(warf, pd.Series):
        rating_scores = warf.apply(_get_scores_from_warf_db)
        rating_scores.name = "rtg_score"
        return rating_scores

    elif isinstance(warf, pd.DataFrame):
        return warf.applymap(_get_scores_from_warf_db).add_prefix("rtg_score_")
