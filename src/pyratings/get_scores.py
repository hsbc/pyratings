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

| Moody’s |  S&P | Fitch |  ICE | DBRS | Bloomberg | Score |  WARF | MinWARF* | MaxWARF* |
|:-------:|:----:|:-----:|:----:|:----:|:---------:|------:|------:|---------:|---------:|
|   Aaa   |  AAA |  AAA  |  AAA |  AAA |    AAA    |     1 |     1 |        1 |        5 |
|   Aa1   |  AA+ |  AA+  |  AA+ |  AAH |    AA+    |     2 |    10 |        5 |       15 |
|   Aa2   |  AA  |   AA  |  AA  |  AA  |     AA    |     3 |    20 |       15 |       30 |
|   Aa3   |  AA- |  AA-  |  AA- |  AAL |    AA-    |     4 |    40 |       30 |       55 |
|    A1   |  A+  |   A+  |  A+  |  AH  |     A+    |     5 |    70 |       55 |       95 |
|    A2   |   A  |   A   |   A  |   A  |     A     |     6 |   120 |       95 |      150 |
|    A3   |  A-  |   A-  |  A-  |  AL  |     A-    |     7 |   180 |      150 |      220 |
|   Baa1  | BBB+ |  BBB+ | BBB+ | BBBH |    BBB+   |     8 |   260 |      220 |      310 |
|   Baa2  |  BBB |  BBB  |  BBB |  BBB |    BBB    |     9 |   360 |      310 |      485 |
|   Baa3  | BBB- |  BBB- | BBB- | BBBL |    BBB-   |    10 |   610 |      485 |      775 |
|   Ba1   |  BB+ |  BB+  |  BB+ |  BBH |    BB+    |    11 |   940 |      775 |     1145 |
|   Ba2   |  BB  |   BB  |  BB  |  BB  |     BB    |    12 |  1350 |     1145 |     1558 |
|   Ba3   |  BB- |  BB-  |  BB- |  BBL |    BB-    |    13 |  1766 |     1558 |     1993 |
|    B1   |  B+  |   B+  |  B+  |  BH  |     B+    |    14 |  2220 |     1993 |     2470 |
|    B2   |   B  |   B   |   B  |   B  |     B     |    15 |  2720 |     2470 |     3105 |
|    B3   |  B-  |   B-  |  B-  |  BL  |     B-    |    16 |  3490 |     3105 |     4130 |
|   Caa1  | CCC+ |  CCC+ | CCC+ | CCCH |    CCC+   |    17 |  4770 |     4130 |     5635 |
|   Caa2  |  CCC |  CCC  |  CCC |  CCC |    CCC    |    18 |  6500 |     5635 |     7285 |
|   Caa3  | CCC- |  CCC- | CCC- | CCCL |    CCC-   |    19 |  8070 |     7285 |     9034 |
|    Ca   |  CC  |   CC  |  CC  |  CC  |     CC    |    20 |  9998 |     9034 |   9998.5 |
|    C    |   C  |   C   |   C  |   C  |     C     |    21 |  9999 |   9998.5 |   9999.5 |
|    D    |   D  |   D   |   D  |   D  |    DDD    |    22 | 10000 |   9999.5 |    10000 |

`MinWARF` is inclusive, while `MaxWARF` is exclusive.

For short-term ratings, the following translation table will be used:

| Moody’s | S&P  | Fitch |    DBRS    | Score |
|:-------:|:----:|:-----:|:----------:| -----:|
|   P-1   | A-1+ |  F1+  | R-1 (high) |     1 |
|         |      |       | R-1 (mid)  |     2 |
|         |      |       | R-1 (low)  |     3 |
|         | A-1  |  F1   | R-2 (high) |     5 |
|         |      |       | R-2 (mid)  |     6 |
|   P-2   | A-2  |  F2   | R-2 (low)  |     7 |
|         |      |       | R-3 (high) |     8 |
|   P-3   | A-3  |  F3   | R-3 (mid)  |     9 |
|         |      |       | R-3 (low)  |    10 |
|   NP    |  B   |       |    R-4     |    12 |
|         |      |       |    R-5     |    15 |
|         |  C   |       |            |    18 |
|         |  D   |       |     D      |    22 |

"""  # noqa: B950

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
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

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
    Converting a single rating:

    >>> get_scores_from_ratings("BBB-", "S&P", tenor="long-term")
    10

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

        rtg_dict = _get_translation_dict("rtg_to_scores", rating_provider, tenor=tenor)
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

        rtg_dict = _get_translation_dict("rtg_to_scores", rating_provider, tenor=tenor)
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
                    ratings=ratings[col], rating_provider=provider, tenor=tenor
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
