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
            rating_provider=rating_provider,
            valid_rtg_provider=valid_rtg_agncy[tenor],
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
                rating_provider=rating_scores.name,
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )
        else:
            rating_provider = _extract_rating_provider(
                rating_provider=rating_provider,
                valid_rtg_provider=valid_rtg_agncy[tenor],
            )

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
