# Copyright 2022 HSBC Global Asset Management (Deutschland) GmbH
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import importlib.resources as pkg_resources
import sqlite3
from typing import Dict, Hashable, List, Optional, Union

import numpy as np
import pandas as pd

from pyratings import resources

RATINGS_DB = pkg_resources.files(resources).joinpath("Ratings.db")
VALUE_ERROR_PROVIDER_MANDATORY = "'rating_provider' must not be None."


# --- get_pure_ratings -----------------------------------------------------------------
def get_pure_ratings(
    ratings: Union[str, pd.Series, pd.DataFrame]
) -> Union[str, pd.Series, pd.DataFrame]:
    """Removes rating watches/outlooks.

    Parameters
    ----------
    ratings
        Rating may contain watch, such as `AA- *+`, `BBB+ (CwNegative)`.
        Outlook/watch should be seperated by a blank from the actual rating.

    Returns
    -------
    Union[str, pd.Series, pd.DataFrame]
        String, Series, or DataFrame with regular ratings stripped off of watches.
        The name of the resulting Series or the columns of the returning DataFrame will
        be suffixed with `_clean`.

    Examples
    --------
    Cleaning a single rating:

    >>> get_pure_ratings("AA- *+")
    'AA-'

    >>> get_pure_ratings("Au")
    'A'

    Cleaning a `pd.Series`:

    >>> import pandas as pd

    >>> rating_series=pd.Series(
    ...    data=[
    ...        "BB+ *-",
    ...        "BBB *+",
    ...        np.nan,
    ...        "AA- (Developing)",
    ...        np.nan,
    ...        "CCC+ (CwPositive)",
    ...        "BB+u",
    ...    ],
    ...    name="rtg_SP",
    ... )
    >>> get_pure_ratings(rating_series)
    0     BB+
    1     BBB
    2     NaN
    3     AA-
    4     NaN
    5    CCC+
    6     BB+
    Name: rtg_SP_clean, dtype: object

    Cleaning a `pd.DataFrame`:

    >>> rtg_df = pd.DataFrame(
    ...    data={
    ...        "rtg_SP": [
    ...            "BB+ *-",
    ...            "BBB *+",
    ...            np.nan,
    ...            "AA- (Developing)",
    ...            np.nan,
    ...            "CCC+ (CwPositive)",
    ...            "BB+u",
    ...        ],
    ...        "rtg_Fitch": [
    ...            "BB+ *-",
    ...            "BBB *+",
    ...            pd.NA,
    ...            "AA- (Developing)",
    ...            np.nan,
    ...            "CCC+ (CwPositive)",
    ...            "BB+u",
    ...        ],
    ...    },
    ... )
    >>> get_pure_ratings(rtg_df)
      rtg_SP_clean rtg_Fitch_clean
    0          BB+             BB+
    1          BBB             BBB
    2          NaN            <NA>
    3          AA-             AA-
    4          NaN             NaN
    5         CCC+            CCC+
    6          BB+             BB+

    """
    if isinstance(ratings, str):
        ratings = ratings.split()[0]
        ratings = ratings.rstrip("uU")
        return ratings

    elif isinstance(ratings, pd.Series):
        # identify string occurrences
        isstring = ratings.apply(type).eq(str)

        # strip string after occurrence of very first blank and strip character 'u',
        # which has usually been added without a blank
        ratings[isstring] = ratings[isstring].str.split().str[0]
        ratings[isstring] = ratings[isstring].str.rstrip("uU")
        ratings.name = f"{ratings.name}_clean"
        return ratings

    elif isinstance(ratings, pd.DataFrame):
        # Recursive call of `get_pure_ratings`
        return pd.concat(
            [get_pure_ratings(ratings=ratings[col]) for col in ratings.columns], axis=1
        )


# --- get best/worst ratings -----------------------------------------------------------
def get_best_ratings(
    ratings: pd.DataFrame,
    rating_provider_input: List[str] = None,
    rating_provider_output: str = "S&P",
    tenor: str = "long-term",
) -> pd.Series:
    """Computes the best rating on a security level basis across different rating
    agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within dataframe. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider` will be inferred from the dataframe columns.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.
    tenor
        Indicates wheter long- or short-term ratings will be used.

    Returns
    -------
    pd.Series
        Series of best ratings on a security level basis.

    See Also
    --------
    get_second_best_ratings
    get_worst_ratings

    Examples
    --------
    >>> import pandas as pd

    >>> ratings_df = pd.DataFrame(
    ...     data=(
    ...         {
    ...             "rating_S&P": ['AAA', 'AA-', 'AA+', 'BB-', 'C'],
    ...             "rating_Moody's": ['Aa1', 'Aa3', 'Aa2', 'Ba3', 'Ca'],
    ...             "rating_Fitch": ['AA-', 'AA-', 'AA-', 'B+', 'C'],
    ...         }
    ...     )
    ... )
    >>> get_best_ratings(ratings_df, rating_provider_input=["S&P", "Moody", "Fitch"])
    0    AAA
    1    AA-
    2    AA+
    3    BB-
    4    CC
    Name: best_rtg, dtype: object

    """
    rating_provider_output = _extract_rating_provider(rating_provider_output, tenor)

    # translate ratings -> scores
    rating_scores_df = get_scores_from_ratings(
        ratings, rating_provider=rating_provider_input, tenor=tenor
    )

    # determine lowest ratings score (indicates best rating) and convert to ratings
    best_ratings_series = get_ratings_from_scores(
        rating_scores=rating_scores_df.min(axis=1),
        rating_provider=rating_provider_output,
        tenor=tenor,
    )
    best_ratings_series.name = "best_rtg"

    return best_ratings_series


def get_second_best_ratings(
    ratings: pd.DataFrame,
    rating_provider_input: List[str] = None,
    rating_provider_output: str = "S&P",
    tenor: str = "long-term",
) -> pd.Series:
    """Computes the second-best rating on a security level basis across different rating
    agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within dataframe. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider` will be inferred from the dataframe columns.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.
    tenor
        Indicates wheter long- or short-term ratings will be used.

    Returns
    -------
    pd.Series
        Series of second-best ratings on a security level basis.

    See Also
    --------
    get_best_ratings
    get_worst_ratings

    Examples
    --------
    >>> import pandas as pd

    >>> ratings_df = pd.DataFrame(
    ...     data=(
    ...         {
    ...             "rating_S&P": ['AAA', 'AA-', 'AA+', 'BB-', 'C'],
    ...             "rating_Moody's": ['Aa1', 'Aa3', 'Aa2', 'Ba3', 'Ca'],
    ...             "rating_Fitch": ['AA-', 'AA-', 'AA-', 'B+', 'C'],
    ...         }
    ...     )
    ... )
    >>> get_second_best_ratings(
    ...     ratings_df, rating_provider_input=["S&P", "Moody", "Fitch"]
    ... )
    0    AA+
    1    AA-
    2     AA
    3    BB-
    4      C
    Name: second_best_rtg, dtype: object

    """
    rating_provider_output = _extract_rating_provider(rating_provider_output, tenor)

    # translate ratings -> scores
    rating_scores_df = get_scores_from_ratings(
        ratings, rating_provider=rating_provider_input, tenor=tenor
    )

    # rank scores per security (axis=1)
    scores_ranked_df = rating_scores_df.rank(axis=1, method="first", numeric_only=False)

    # get column with rank of 2, if available, otherwise get column with rank 1
    scores_ranked_ser = rating_scores_df[scores_ranked_df <= 2].max(axis=1)

    # determine lowest ratings score (indicates best rating) and convert to ratings
    second_best_ratings_series = get_ratings_from_scores(
        rating_scores=scores_ranked_ser,
        rating_provider=rating_provider_output,
        tenor=tenor,
    )
    second_best_ratings_series.name = "second_best_rtg"

    return second_best_ratings_series


def get_worst_ratings(
    ratings: pd.DataFrame,
    rating_provider_input: List[str] = None,
    rating_provider_output: str = "S&P",
    tenor: str = "long-term",
) -> pd.Series:
    """Computes the worst rating on a security level basis across different rating
    agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within dataframe. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider` will be inferred from the dataframe columns.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.
    tenor
        Indicates wheter long- or short-term ratings will be used.

    Returns
    -------
    pd.Series
        Series of worst ratings on a security level basis.

    See Also
    --------
    get_best_ratings
    get_second_best_ratings

    Examples
    --------
    >>> import pandas as pd

    >>> ratings_df = pd.DataFrame(
    ...     data=(
    ...         {
    ...             "rating_S&P": ['AAA', 'AA-', 'AA+', 'BB-', 'C'],
    ...             "rating_Moody's": ['Aa1', 'Aa3', 'Aa2', 'Ba3', 'Ca'],
    ...             "rating_Fitch": ['AA-', 'AA-', 'AA-', 'B+', 'C'],
    ...         }
    ...     )
    ... )
    >>> get_worst_ratings(ratings_df, rating_provider_input=["S&P", "Moody", "Fitch"])
    0    AA-
    1    AA-
    2    AA-
    3     B+
    4      C
    Name: worst_rtg, dtype: object

    """
    rating_provider_output = _extract_rating_provider(rating_provider_output, tenor)

    # translate ratings -> scores
    rating_scores_df = get_scores_from_ratings(
        ratings, rating_provider=rating_provider_input, tenor=tenor
    )

    # determine highest ratings score (indicates worst rating) and convert to ratings
    worst_ratings_series = get_ratings_from_scores(
        rating_scores=rating_scores_df.max(axis=1),
        rating_provider=rating_provider_output,
        tenor=tenor,
    )
    worst_ratings_series.name = "worst_rtg"

    return worst_ratings_series


# --- get_scores -----------------------------------------------------------------------
def get_scores_from_ratings(
    ratings: Union[str, pd.Series, pd.DataFrame],
    rating_provider: Optional[Union[str, List[str]]] = None,
    tenor: str = "long-term",
) -> Union[int, pd.Series, pd.DataFrame]:
    """Converts regular ratings into numerical rating scores.

    Parameters
    ----------
    ratings
        Ratings to be translated into rating scores.
    rating_provider
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider` will be inferred from the series name or dataframe
        columns.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    Union[int, pd.Series, pd.DataFrame]
        Rating scores

    Raises
    ------
    ValueError
        If providing a single rating and `rating_provider` is None.

    See Also
    --------
    get_scores_from_warf
    get_ratings_from_scores
    get_ratings_from_warf
    get_warf_from_scores
    get_warf_from_ratings

    Notes
    -----
    For long-term ratings, the following translation table will be used:

    # noqa
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    | Moody’s |  S&P | Fitch |  ICE | DBRS | Bloomberg | Score |  WARF | MinWARF* | MaxWARF* |
    +=========+======+=======+======+======+===========+=======+=======+==========+==========+
    |   Aaa   |  AAA |  AAA  |  AAA |  AAA |    AAA    |     1 |     1 |        1 |        5 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Aa1   |  AA+ |  AA+  |  AA+ |  AAH |    AA+    |     2 |    10 |        5 |       15 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Aa2   |  AA  |   AA  |  AA  |  AA  |     AA    |     3 |    20 |       15 |       30 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Aa3   |  AA- |  AA-  |  AA- |  AAL |    AA-    |     4 |    40 |       30 |       55 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    A1   |  A+  |   A+  |  A+  |  AH  |     A+    |     5 |    70 |       55 |       95 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    A2   |   A  |   A   |   A  |   A  |     A     |     6 |   120 |       95 |      150 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    A3   |  A-  |   A-  |  A-  |  AL  |     A-    |     7 |   180 |      150 |      220 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Baa1  | BBB+ |  BBB+ | BBB+ | BBBH |    BBB+   |     8 |   260 |      220 |      310 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Baa2  |  BBB |  BBB  |  BBB |  BBB |    BBB    |     9 |   360 |      310 |      485 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Baa3  | BBB- |  BBB- | BBB- | BBBL |    BBB-   |    10 |   610 |      485 |      775 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Ba1   |  BB+ |  BB+  |  BB+ |  BBH |    BB+    |    11 |   940 |      775 |     1145 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Ba2   |  BB  |   BB  |  BB  |  BB  |     BB    |    12 |  1350 |     1145 |     1558 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Ba3   |  BB- |  BB-  |  BB- |  BBL |    BB-    |    13 |  1766 |     1558 |     1993 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    B1   |  B+  |   B+  |  B+  |  BH  |     B+    |    14 |  2220 |     1993 |     2470 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    B2   |   B  |   B   |   B  |   B  |     B     |    15 |  2720 |     2470 |     3105 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    B3   |  B-  |   B-  |  B-  |  BL  |     B-    |    16 |  3490 |     3105 |     4130 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Caa1  | CCC+ |  CCC+ | CCC+ | CCCH |    CCC+   |    17 |  4770 |     4130 |     5635 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Caa2  |  CCC |  CCC  |  CCC |  CCC |    CCC    |    18 |  6500 |     5635 |     7285 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |   Caa3  | CCC- |  CCC- | CCC- | CCCL |    CCC-   |    19 |  8070 |     7285 |     9034 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    Ca   |  CC  |   CC  |  CC  |  CC  |     CC    |    20 |  9998 |     9034 |   9998.5 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    C    |   C  |   C   |   C  |   C  |     C     |    21 |  9999 |   9998.5 |   9999.5 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+
    |    D    |   D  |   D   |   D  |   D  |    DDD    |    22 | 10000 |   9999.5 |    10000 |
    +---------+------+-------+------+------+-----------+-------+-------+----------+----------+

    `MinWARF` is inclusive, while `MaxWARF` is exclusive.

    For short-term ratings, the following translation table will be used:

    +---------+------+-------+------------+-------+
    | Moody's |  S&P | Fitch |    DBRS    | Score |
    +=========+======+=======+============+=======+
    |   P-1   | A-1+ |  F1+  | R-1 (high) |     1 |
    +---------+------+-------+------------+-------+
    |   ---   |  --- |  ---  |  R-1 (mid) |     2 |
    +---------+------+-------+------------+-------+
    |   ---   |  --- |  ---  |  R-1 (low) |     3 |
    +---------+------+-------+------------+-------+
    |   ---   |  A-1 |   F1  | R-2 (high) |     5 |
    +---------+------+-------+------------+-------+
    |   ---   |  --- |  ---  |  R-2 (mid) |     6 |
    +---------+------+-------+------------+-------+
    |   P-2   |  A-2 |   F2  |  R-2 (low) |     7 |
    +---------+------+-------+------------+-------+
    |   ---   |  --- |  ---  | R-3 (high) |     8 |
    +---------+------+-------+------------+-------+
    |   P-3   |  A-3 |   F3  |  R-3 (mid) |     9 |
    +---------+------+-------+------------+-------+
    |   ---   |  --- |  ---  |  R-3 (low) |    10 |
    +---------+------+-------+------------+-------+
    |    NP   |   B  |  ---  |     R-4    |    12 |
    +---------+------+-------+------------+-------+
    |   ---   |  --- |  ---  |     R-5    |    15 |
    +---------+------+-------+------------+-------+
    |   ---   |   C  |  ---  |     ---    |    18 |
    +---------+------+-------+------------+-------+
    |   ---   |   D  |  ---  |      D     |    22 |
    +---------+------+-------+------------+-------+

    Examples
    --------
    Converting a single rating:

    >>> get_scores_from_ratings("BBB-", "S&P", tenor="long-term")
    10

    Converting a ``pd.Series`` of ratings:

    >>> import pandas as pd
    >>> ratings_series = pd.Series(data=["Baa1", "C", "NR", "WD", "D", "B1", "SD"])
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
    ...     data=[["BB+", "B3", "BBB-"], ["AA-", "Aa1", "AAA"], ["D", "NR", "D"]]
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
       rtg_score_Fitch  rtg_score_Bloomberg  rtg_score_DBRS
    0               11                 16.0             NaN
    1                4                  2.0             1.0
    2               22                  NaN            22.0

    """
    if isinstance(ratings, str):
        if rating_provider is None:
            raise ValueError(VALUE_ERROR_PROVIDER_MANDATORY)

        rating_provider = _extract_rating_provider(
            rating_provider=rating_provider, tenor=tenor
        )

        rtg_dict = _get_translation_dict("rtg_to_scores", rating_provider, tenor=tenor)
        return rtg_dict.get(ratings, pd.NA)

    elif isinstance(ratings, pd.Series):
        if rating_provider is None:
            rating_provider = _extract_rating_provider(
                rating_provider=ratings.name, tenor=tenor
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider, tenor=tenor
            )

        rtg_dict = _get_translation_dict("rtg_to_scores", rating_provider, tenor=tenor)
        return pd.Series(
            data=ratings.map(rtg_dict), name=f"rtg_score_{rating_provider}"
        )

    elif isinstance(ratings, pd.DataFrame):
        if rating_provider is None:
            rating_provider = _extract_rating_provider(
                rating_provider=ratings.columns.to_list(), tenor=tenor
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider, tenor=tenor
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
    """Converts WARFs into numerical rating scores.

    Parameters
    ----------
    warf
        Weighted average rating factor (WARF).

    Returns
    -------
    Union[int, float, pd.Series, pd.DataFrame]
        Numerical rating score.

    See Also
    --------
    get_scores_from_ratings
    get_ratings_from_scores
    get_ratings_from_warf
    get_warf_from_scores
    get_warf_from_ratings

    Notes
    -----
    Compare notes in :py:func:`get_scores_from_ratings` for translation tables.

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

    def _get_scores_from_warf_db(wrf) -> Union[int, float]:
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


# --- get_ratings ----------------------------------------------------------------------
def get_ratings_from_scores(
    rating_scores: Union[int, float, pd.Series, pd.DataFrame],
    rating_provider: Optional[Union[str, List[str]]] = None,
    tenor: str = "long-term",
) -> Union[str, pd.Series, pd.DataFrame]:
    """Converts numerical rating scores into regular ratings.

    Parameters
    ----------
    rating_scores
        Numerical rating scores
    rating_provider
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider` will be inferred from the series name or dataframe
        columns.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    Union[str, pd.Series, pd.DataFrame]
        Regular ratings according to `rating_provider`'s rating scale.

    Raises
    ------
    ValueError
        If providing a single rating score and `rating_provider` is None.

    See Also
    --------
    get_scores_from_ratings
    get_scores_from_warf
    get_ratings_from_warf
    get_warf_from_scores
    get_warf_from_ratings

    Notes
    -----
    Compare notes in :py:func:`get_scores_from_ratings` for translation tables.

    Examples
    --------
    Converting a single rating score:

    >>> get_ratings_from_scores(rating_scores=9, rating_provider="Fitch")
    'BBB'

    >>> get_ratings_from_scores(
    ...     rating_scores=5, rating_provider="S&P", tenor="short-term"
    ... )
    'A-1'

    Converting a ``pd.Series`` with scores:

    >>> import pandas as pd
    >>> rating_scores_series = pd.Series(data=[5, 7, 1, np.nan, 22, pd.NA])
    >>> get_ratings_from_scores(
    ...     rating_scores=rating_scores_series,
    ...     rating_provider="Moody's",
    ...     tenor="long-term",
    ... )
    0     A1
    1     A3
    2    Aaa
    3    NaN
    4      D
    5    NaN
    Name: rtg_Moody, dtype: object

    Providing a ``pd.Series`` without specifying a `rating_provider`:

    >>> rating_scores_series = pd.Series(
    ...     data=[5, 7, 1, np.nan, 22, pd.NA],
    ...     name="Moody",
    ... )
    >>> get_ratings_from_scores(rating_scores=rating_scores_series)
    0     A1
    1     A3
    2    Aaa
    3    NaN
    4      D
    5    NaN
    Name: rtg_Moody, dtype: object

    Converting a ``pd.DataFrame`` with scores:

    >>> rating_scores_df = pd.DataFrame(
    ...     data=[[11, 16, "foo"], [4, 2, 1], [22, "bar", 22]]
    ... )
    >>> get_ratings_from_scores(
    ...     rating_scores=rating_scores_df,
    ...     rating_provider=["Fitch", "Bloomberg", "DBRS"],
    ...     tenor="long-term",
    ... )
      rtg_Fitch rtg_Bloomberg rtg_DBRS
    0       BB+            B-      NaN
    1       AA-           AA+      AAA
    2         D           NaN        D

    When providing a ``pd.DataFrame`` without explicitly providing the
    `rating_provider`, they will be inferred by the dataframe's columns.

    >>> rating_scores_df = pd.DataFrame(
    ...     data={
    ...         "rtg_fitch": [11, 4, 22],
    ...         "rtg_Bloomberg": [16, 2, "foo"],
    ...         "DBRS Ratings": ["bar", 1, 22],
    ...     }
    ... )
    >>> get_ratings_from_scores(rating_scores=rating_scores_df)
      rtg_Fitch rtg_Bloomberg rtg_DBRS
    0       BB+            B-      NaN
    1       AA-           AA+      AAA
    2         D           NaN        D

    """
    if isinstance(rating_scores, (int, float, np.number)):
        if rating_provider is None:
            raise ValueError(VALUE_ERROR_PROVIDER_MANDATORY)

        rating_provider = _extract_rating_provider(
            rating_provider=rating_provider, tenor=tenor
        )

        rtg_dict = _get_translation_dict(
            "scores_to_rtg", rating_provider=rating_provider, tenor=tenor
        )

        if not np.isnan(rating_scores):
            rating_scores = round(rating_scores)
            return rtg_dict.get(rating_scores, pd.NA)

    elif isinstance(rating_scores, pd.Series):
        if rating_provider is None:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_scores.name, tenor=tenor
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider, tenor=tenor
            )

        if rating_provider in ["Bloomberg", "ICE"]:
            assert (
                tenor == "long-term"
            ), f"{rating_provider} does not provide short-term ratings"

        rtg_dict = _get_translation_dict("scores_to_rtg", rating_provider, tenor=tenor)

        # round element to full integer, if element is number
        rating_scores = rating_scores.apply(
            lambda x: np.round(x, 0) if isinstance(x, (int, float, np.number)) else x
        )

        return pd.Series(
            data=rating_scores.map(rtg_dict), name=f"rtg_{rating_provider}"
        )

    elif isinstance(rating_scores, pd.DataFrame):
        if rating_provider is None:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_scores.columns.to_list(), tenor=tenor
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider, tenor=tenor
            )

        # Recursive call of 'get_ratings_from_score' for every column in dataframe
        return pd.concat(
            [
                get_ratings_from_scores(
                    rating_scores=rating_scores[col],
                    rating_provider=provider,
                    tenor=tenor,
                )
                for col, provider in zip(rating_scores.columns, rating_provider)
            ],
            axis=1,
        )


def get_ratings_from_warf(
    warf: Union[int, float, pd.Series, pd.DataFrame],
    rating_provider: Optional[Union[str, List[str]]] = None,
) -> Union[str, pd.Series, pd.DataFrame]:
    """Converts WARFs into regular ratings.

    Parameters
    ----------
    warf
        Numerical WARF.
    rating_provider
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

    Returns
    -------
    Union[str, pd.Series, pd.DataFrame]
        Regular rating according to `rating_provider`'s rating scale.

    See Also
    --------
    get_scores_from_ratings
    get_scores_from_warf
    get_ratings_from_scores
    get_warf_from_scores
    get_warf_from_ratings

    Notes
    -----
    Internally, `warf` will be converted into a rating score.

    Compare notes in :py:func:`get_scores_from_ratings` for translation tables.

    Examples
    --------
    Converting a single WARF:

    >>> get_ratings_from_warf(warf=610, rating_provider="DBRS")
    'BBBL'

    >>> get_ratings_from_warf(warf=1234.5678, rating_provider="ICE")
    'BB'

    Converting a ``pd.Series`` with WARFs:

    >>> import pandas as pd
    >>> warf_series = pd.Series(data=[90, 218.999, 1, np.nan, 10000, pd.NA])
    >>> get_ratings_from_warf(
    ...     warf=warf_series,
    ...     rating_provider="Moody's",
    ... )
    0     A1
    1     A3
    2    Aaa
    3    NaN
    4      D
    5    NaN
    Name: rtg_Moody, dtype: object

    Converting a ``pd.DataFrame`` with WARFs:

    >>> warf_df = pd.DataFrame(
    ...     data=[[940, 4000, "foo"], [54, 13.5, 1], [10000, "bar", 9999]]
    ... )
    >>> get_ratings_from_warf(
    ...     warf=warf_df,
    ...     rating_provider=["Fitch", "Bloomberg", "DBRS"],
    ... )
      rtg_Fitch rtg_Bloomberg rtg_DBRS
    0       BB+            B-      NaN
    1       AA-           AA+      AAA
    2         D           NaN        C

    """
    if isinstance(warf, (int, float, np.number)):
        if rating_provider is None:
            raise ValueError(VALUE_ERROR_PROVIDER_MANDATORY)

        rating_provider = _extract_rating_provider(
            rating_provider=rating_provider, tenor="long-term"
        )

        rating_scores = get_scores_from_warf(warf=warf)
        return get_ratings_from_scores(
            rating_scores=rating_scores,
            rating_provider=rating_provider,
            tenor="long-term",
        )

    elif isinstance(warf, (pd.Series, pd.DataFrame)):
        rating_scores = get_scores_from_warf(warf=warf)
        return get_ratings_from_scores(
            rating_scores=rating_scores,
            rating_provider=rating_provider,
            tenor="long-term",
        )


# --- get_warf -------------------------------------------------------------------------
def get_warf_from_scores(
    rating_scores: Union[int, float, pd.Series, pd.DataFrame],
) -> Union[int, pd.Series, pd.DataFrame]:
    """Converts numerical rating scores to numerical WARFs.

    Parameters
    ----------
    rating_scores
        Numerical rating scores.

    Returns
    -------
    Union[int, pd.Series, pd.DataFrame
        Numerical WARFs.

    See Also
    --------
    get_scores_from_ratings
    get_scores_from_warf
    get_ratings_from_scores
    get_ratings_from_warf
    get_warf_from_ratings

    Notes
    -----
    Compare notes in :py:func:`get_scores_from_ratings` for translation tables.

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
        return pd.Series(data=rating_scores.map(warf_dict), name="warf")
    elif isinstance(rating_scores, pd.DataFrame):
        return rating_scores.apply(lambda x: x.map(warf_dict)).add_prefix("warf_")


def get_warf_from_ratings(
    ratings: Union[str, pd.Series, pd.DataFrame],
    rating_provider: Optional[Union[str, List[str]]] = None,
) -> Union[int, pd.Series, pd.DataFrame]:
    """Converts regular ratings to numerical WARFs.

    Parameters
    ----------
    ratings
        Regular ratings to be translated into WARFs.
    rating_provider
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider` will be inferred from the series name or dataframe
        columns.

    Returns
    -------
    Union[int, pd.Series, pd.DataFrame]
        Numerical WARF.

    See Also
    --------
    get_scores_from_ratings
    get_scores_from_warf
    get_ratings_from_scores
    get_ratings_from_warf
    get_warf_from_scores

    Notes
    -----
    Internally, `ratings` will be converted into rating scores.

    Compare notes in :py:func:`get_scores_from_ratings` for translation tables.

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
    Name: warf, dtype: float64

    Converting a ``pd.DataFrame`` with ratings:

    >>> ratings_df = pd.DataFrame(
    ...     data=[["BB+", "B-", "foo"], ["AA-", "AA+", "AAA"], ["D", "bar", "C"]]
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
       warf_Fitch  warf_Bloomberg  warf_DBRS
    0         940          3490.0        NaN
    1          40            10.0        1.0
    2       10000             NaN     9999.0

    """
    if rating_provider is not None:
        rating_provider = _extract_rating_provider(
            rating_provider=rating_provider, tenor="long-term"
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
        try:  # only successful if `rating_scores` is ``pd.DataFrame``
            rating_scores.columns = rating_scores.columns.str.lstrip("rtg_score_")
        except AttributeError:
            pass
        return get_warf_from_scores(rating_scores=rating_scores)


def get_weighted_average(data: pd.Series, weights: pd.Series) -> float:
    """
    Computes weighted average.

    Parameters
    ----------
    data
        Contains numerical values.
    weights
        Contains weights (between 0 and 1) with respect to data.

    Returns
    -------
    float
        Weighted average data.

    Notes
    -----
    Computing the weighted average is simply the sumproduct of `data` and `weights`.
    ``nan`` in `data` will be excluded from calculating the weighted average. All
    corresponding weights will be ignored. As a matter of fact, the remaining
    weights will be upscaled so that the weights of all ``non-nan`` rows in `data` will
    sum up to 1 (100%).

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd

    >>> rtg_scores = pd.Series(data=[5, 7, 9])
    >>> wgt = pd.Series(data=[0.5, 0.3, 0.2])
    >>> get_weighted_average(data=rtg_scores, weights=wgt)
    6.4

    >>> warf = pd.Series(data=[500, 735, np.nan, 93, np.nan])
    >>> wgt = pd.Series(data=[0.4, 0.1, 0.1, 0.2, 0.2])
    >>> get_weighted_average(data=warf, weights=wgt)
    417.29
    """
    # find indices in warf that correspond to np.nan
    idx_nan = data[pd.isna(data)].index

    # sum weights of securities with an actual rating, i.e. rating is not NaN
    weights_non_nan = 1 - sum(weights.loc[idx_nan])

    # upscale to 100%
    weights_upscaled = weights / weights_non_nan

    return data.fillna(0).dot(weights_upscaled)


def get_warf_buffer(warf: Union[float, int]) -> Union[float, int]:
    """
    Computes WARF buffer.

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


def _assert_rating_provider(rating_provider, tenor: str) -> None:
    """Asserts that valid rating provider has been submitted."""
    if isinstance(rating_provider, str):
        rating_provider = [rating_provider]
    if tenor == "long-term":
        rtg_agencies = ("Moody", "SP", "Fitch", "Bloomberg", "DBRS", "ICE")
        assert set(rating_provider).issubset(rtg_agencies), (
            "rating_provider must be in "
            "['Moody', 'SP', 'Fitch', 'Bloomberg', 'DBRS', 'ICE']."
        )
    elif tenor == "short-term":
        rtg_agencies = ("Moody", "SP", "Fitch", "DBRS")
        assert set(rating_provider).issubset(
            rtg_agencies
        ), "rating_provider must be in ['Moody', 'SP', 'Fitch', 'DBRS']."


def _extract_rating_provider(
    rating_provider: Union[str, List[str], Hashable],
    tenor: str,
) -> Union[str, List[str]]:
    """Extracts valid rating providers from a given list.

    It is meant to extract rating providers from the column headings of a
    ``pd.DataFrame``. For example, let's assume some rating column headers are
    ["rating_fitch", "S&P rating", "BLOOMBERG composite rating"]. The function would
    then return a list of valid rating providers, namely ["Fitch", "SP", "Bloomberg"].

    Parameters
    ----------
    rating_provider
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

    Returns
    -------
    Union[str, List[str]]
        str or List[str] with valid rating providers.

    Raises
    ------
    AssertionError
        If ``rating_provider`` contains an invalid entry.

    Examples
    --------
    >>> _extract_rating_provider("S&P", tenor="long-term")
    'SP'

    >>> _extract_rating_provider("rtg_DBRS", tenor="short-term")
    'DBRS'

    You can also provide a list of strings.

    >>> _extract_rating_provider(
    ...     ["Fitch ratings", "rating_SP", "ICE"], tenor="long-term"
    ... )
    ['Fitch', 'SP', 'ICE']

    """
    valid_providers = ["fitch", "moody", "sp", "s&p", "bloomberg", "dbrs", "ice"]
    provider_map = {
        "fitch": "Fitch",
        "moody": "Moody",
        "sp": "SP",
        "s&p": "SP",
        "bloomberg": "Bloomberg",
        "dbrs": "DBRS",
        "ice": "ICE",
    }
    if isinstance(rating_provider, str):
        rating_provider = [rating_provider]

    for i, provider in enumerate(rating_provider):
        if not any(x in provider.lower() for x in valid_providers):
            raise AssertionError(
                f"'{provider}' is not a valid rating provider. 'rating_provider' must "
                f"be in ['Moody', 'SP', 'Fitch', 'Bloomberg', 'DBRS', 'ICE']."
            )
        for valid_provider in valid_providers:
            if valid_provider in provider.lower():
                rating_provider[i] = provider_map[valid_provider]

    _assert_rating_provider(rating_provider, tenor)

    if len(rating_provider) > 1:
        return rating_provider
    else:
        return rating_provider[0]


def _get_translation_dict(
    translation_table: str, rating_provider: str = None, tenor: str = "long-term"
) -> Dict:
    """Loads translation dictionaries from SQLite database."""

    if rating_provider == "SP":
        rating_provider = "S&P"
    if rating_provider == "Moody":
        rating_provider = "Moody's"

    # connect to database
    connection = sqlite3.connect(RATINGS_DB)
    cursor = connection.cursor()

    # create SQL query
    sql_query = None
    if translation_table in ["rtg_to_scores", "ratings_to_scores"]:
        sql_query = (
            "SELECT Rating, RatingScore FROM v_RatingsToScores "
            "WHERE RatingProvider=? and Tenor=?"
        )
    elif translation_table in ["scores_to_rtg", "scores_to_ratings"]:
        sql_query = (
            "SELECT RatingScore, Rating FROM v_ScoresToRatings "
            "WHERE RatingProvider=? and Tenor=?"
        )
    elif translation_table in ["scores_to_warf"]:
        sql_query = "SELECT RatingScore, WARF FROM WARFs"

    # execute SQL query
    if translation_table in [
        "rtg_to_scores",
        "ratings_to_scores",
        "scores_to_rtg",
        "scores_to_ratings",
    ]:
        cursor.execute(sql_query, (rating_provider, tenor))
    else:
        cursor.execute(sql_query)
    translation_dict = dict(cursor.fetchall())

    # close database connection
    connection.close()

    return translation_dict
