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

"""Module contains functions to consolidate ratings from different rating agencies."""

from typing import List

import pandas as pd

from pyratings.get_ratings import get_ratings_from_scores
from pyratings.get_scores import get_scores_from_ratings
from pyratings.utils import _extract_rating_provider


def get_best_ratings(
    ratings: pd.DataFrame,
    rating_provider_input: List[str] = None,
    rating_provider_output: str = "S&P",
    tenor: str = "long-term",
) -> pd.Series:
    """Compute the best rating on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider_input` will be inferred from the dataframe column
        names.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    pd.Series
        Best ratings on a security level basis.

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

    # determine the lowest ratings score (indicates best rating) and convert to ratings
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
    """Compute the second-best rating on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider_input` will be inferred from the dataframe column
        names.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    pd.Series
        Second-best ratings on a security level basis.

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

    # determine the lowest ratings score (indicates best rating) and convert to ratings
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
    """Compute the worst rating on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.

        If None, `rating_provider_innput` will be inferred from the dataframe column
        names.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    pd.Series
        Worst ratings on a security level basis.

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

    # determine the highest ratings score (indicates worst rating) and convert to
    # ratings
    worst_ratings_series = get_ratings_from_scores(
        rating_scores=rating_scores_df.max(axis=1),
        rating_provider=rating_provider_output,
        tenor=tenor,
    )
    worst_ratings_series.name = "worst_rtg"

    return worst_ratings_series
