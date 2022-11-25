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

"""Module contains functions to translate rating scores / WARF into ratings.

All functions use the following table in order to translate between
numerical scores/WARF and long-term ratings.

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

For short-term ratings, the rating will be translated into an equivalent long-term
rating score. The translation will depend on the a "translation strategy". The following
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

"""  # noqa: B950

from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from pyratings.get_scores import get_scores_from_warf
from pyratings.utils import (
    VALUE_ERROR_PROVIDER_MANDATORY,
    _extract_rating_provider,
    _get_translation_dict,
    valid_rtg_agncy,
)


def get_ratings_from_scores(
    rating_scores: Union[int, float, pd.Series, pd.DataFrame],
    rating_provider: Optional[Union[str, List[str]]] = None,
    tenor: str = "long-term",
    short_term_strategy: Optional[str] = None,
) -> Union[str, pd.Series, pd.DataFrame]:
    """Convert numerical rating scores into regular ratings.

    Parameters
    ----------
    rating_scores
        Numerical rating score(s).
    rating_provider
        Should contain any valid rating provider out of {"Fitch", "Moody's", "S&P",
        "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider` will be inferred from the series name or dataframe
        column names.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}.
    short_term_strategy
        Will only be used, if `tenor` is "short-term". Choose between three distinct
        strategies in order to translate a long-term rating score into a short-term
        rating. Must be in {"best", "base", "worst"}.

        Compare
        https://hsbc.github.io/pyratings/short-term-rating/#there's-one-more-catch...

        - Strategy 1 (best):
          Always choose the best possible short-term rating. That's the optimistic
          approach.
        - Strategy 2 (base-case):
          Always choose the short-term rating that a rating agency would usually assign
          if there aren't any special liquidity issues (positive or negative). That's
          the base-case approach.
        - Strategy 3 (worst):
          Always choose the worst possible short-term rating. That's the conservative
          approach.

    Returns
    -------
    Union[str, pd.Series, pd.DataFrame]
        Regular ratings according to `rating_provider`'s rating scale.

    Raises
    ------
    ValueError
        If providing a single rating score and `rating_provider` is None.

    Examples
    --------
    Converting a single long-term rating score:

    >>> get_ratings_from_scores(rating_scores=9, rating_provider="Fitch")
    'BBB'

    Converting a single short-term rating score with different `short_term_stragey`
    arguments:

    >>> get_ratings_from_scores(
    ...     rating_scores=10,
    ...     rating_provider="DBRS",
    ...     tenor="short-term",
    ...     short_term_strategy="best",
    ... )
    'R-2 M'

    >>> get_ratings_from_scores(
    ...     rating_scores=10,
    ...     rating_provider="DBRS",
    ...     tenor="short-term",
    ...     short_term_strategy="base",
    ... )
    'R-2 L / R-3'

    >>> get_ratings_from_scores(
    ...     rating_scores=10,
    ...     rating_provider="DBRS",
    ...     tenor="short-term",
    ...     short_term_strategy="worst",
    ... )
    'R-3'

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
    if tenor == "short-term" and short_term_strategy is None:
        short_term_strategy = "base"
    if tenor == "short-term" and short_term_strategy not in ["best", "base", "worst"]:
        raise ValueError(
            "Invalid short_term_strategy. Must be in ['best', 'base', 'worst']."
        )

    if isinstance(rating_scores, (int, float, np.number)):
        if rating_provider is None:
            raise ValueError(VALUE_ERROR_PROVIDER_MANDATORY)

        rating_provider = _extract_rating_provider(
            rating_provider=rating_provider,
            valid_rtg_provider=valid_rtg_agncy[tenor],
        )

        rtg_dict = _get_translation_dict(
            "scores_to_rtg",
            rating_provider=rating_provider,
            tenor=tenor,
            st_rtg_strategy=short_term_strategy,
        )

        if not np.isnan(rating_scores):
            rating_scores = int(Decimal(f"{rating_scores}").quantize(0, ROUND_HALF_UP))
            if tenor == "long-term":
                return rtg_dict.get(rating_scores, pd.NA)
            else:
                try:
                    return rtg_dict.loc[
                        (rating_scores >= rtg_dict["MinScore"])
                        & (rating_scores <= rtg_dict["MaxScore"]),
                        "Rating",
                    ].iloc[0]

                except IndexError:
                    return np.nan

    elif isinstance(rating_scores, pd.Series):
        if rating_provider is None:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_scores.name,
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider,
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )

        rtg_dict = _get_translation_dict(
            "scores_to_rtg",
            rating_provider,
            tenor=tenor,
            st_rtg_strategy=short_term_strategy,
        )

        # round element to full integer, if element is number
        rating_scores = rating_scores.apply(
            lambda x: np.round(x, 0) if isinstance(x, (int, float, np.number)) else x
        )

        if tenor == "long-term":
            return pd.Series(
                data=rating_scores.map(rtg_dict), name=f"rtg_{rating_provider}"
            )
        else:
            out = []
            for score in rating_scores:
                try:
                    out.append(
                        rtg_dict.loc[
                            (score >= rtg_dict["MinScore"])
                            & (score <= rtg_dict["MaxScore"]),
                            "Rating",
                        ].iloc[0]
                    )
                except (IndexError, TypeError):
                    out.append(pd.NA)
            return pd.Series(data=out, name=f"rtg_{rating_provider}")

    elif isinstance(rating_scores, pd.DataFrame):
        if rating_provider is None:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_scores.columns.to_list(),
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider,
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )

        # Recursive call of 'get_ratings_from_score' for every column in dataframe
        return pd.concat(
            [
                get_ratings_from_scores(
                    rating_scores=rating_scores[col],
                    rating_provider=provider,
                    tenor=tenor,
                    short_term_strategy=short_term_strategy,
                )
                for col, provider in zip(rating_scores.columns, rating_provider)
            ],
            axis=1,
        )


def get_ratings_from_warf(
    warf: Union[int, float, pd.Series, pd.DataFrame],
    rating_provider: Optional[Union[str, List[str]]] = None,
) -> Union[str, pd.Series, pd.DataFrame]:
    """Convert WARFs into regular ratings.

    Parameters
    ----------
    warf
        Numerical WARF(s).
    rating_provider
        Should contain any valid rating provider out of {"Fitch", "Moody's", "S&P",
        "Bloomberg", "DBRS", "ICE"}.

    Returns
    -------
    Union[str, pd.Series, pd.DataFrame]
        Regular rating(s) according to `rating_provider`'s rating scale.

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
            rating_provider=rating_provider,
            valid_rtg_provider=valid_rtg_agncy["long-term"],
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
