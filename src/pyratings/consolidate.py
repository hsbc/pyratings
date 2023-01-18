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

"""Module contains functions to consolidate ratings from different rating agencies."""

from typing import Literal

import pandas as pd

from pyratings.get_ratings import get_ratings_from_scores
from pyratings.get_scores import get_scores_from_ratings


def get_best_scores(
    ratings: pd.DataFrame,
    rating_provider_input: list[str] = None,
    tenor: Literal["long-term", "short-term"] = "long-term",
) -> pd.Series:
    """Compute the best rating scores on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.

        If None, `rating_provider_input` will be inferred from the dataframe column
        names.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    pd.Series
        Best rating scores on a security level basis.

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
    >>> get_best_scores(
    ...     ratings=ratings_df,
    ...     rating_provider_input=["S&P", "Moody", "Fitch"]
    ... )
    0     1
    1     4
    2     2
    3    13
    4    20
    Name: best_scores, dtype: int64

    """
    rating_scores_df = get_scores_from_ratings(
        ratings=ratings, rating_provider=rating_provider_input, tenor=tenor
    )
    rating_scores_series = rating_scores_df.min(axis=1)
    rating_scores_series.name = "best_scores"

    return rating_scores_series


def get_second_best_scores(
    ratings: pd.DataFrame,
    rating_provider_input: list[str] = None,
    tenor: Literal["long-term", "short-term"] = "long-term",
) -> pd.Series:
    """Compute the second-best scores on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.

        If None, `rating_provider_input` will be inferred from the dataframe column
        names.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    pd.Series
        Second-best scores on a security level basis.

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
    >>> get_second_best_scores(
    ...     ratings_df, rating_provider_input=["S&P", "Moody", "Fitch"]
    ... )
    0     2.0
    1     4.0
    2     3.0
    3    13.0
    4    21.0
    Name: second_best_scores, dtype: float64

    """
    rating_scores_df = get_scores_from_ratings(
        ratings=ratings, rating_provider=rating_provider_input, tenor=tenor
    )

    # rank scores per security (axis=1)
    scores_ranked_df = rating_scores_df.rank(axis=1, method="first", numeric_only=False)

    # get column with rank of 2, if available, otherwise get column with rank 1
    rating_scores_ranked_series = rating_scores_df[scores_ranked_df <= 2].max(axis=1)

    rating_scores_ranked_series.name = "second_best_scores"

    return rating_scores_ranked_series


def get_worst_scores(
    ratings: pd.DataFrame,
    rating_provider_input: list[str] = None,
    tenor: Literal["long-term", "short-term"] = "long-term",
) -> pd.Series:
    """Compute the worst scores on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.

        If None, `rating_provider_innput` will be inferred from the dataframe column
        names.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    pd.Series
        Worst scores on a security level basis.

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
    >>> get_worst_scores(ratings_df, rating_provider_input=["S&P", "Moody", "Fitch"])
    0     4
    1     4
    2     4
    3    14
    4    21
    Name: worst_scores, dtype: int64

    """
    rating_scores_df = get_scores_from_ratings(
        ratings=ratings, rating_provider=rating_provider_input, tenor=tenor
    )
    rating_scores_series = rating_scores_df.max(axis=1)
    rating_scores_series.name = "worst_scores"

    return rating_scores_series


def consolidate_ratings(
    ratings: pd.DataFrame,
    method: Literal["best", "second_best", "worst"] = "worst",
    rating_provider_input: list[str] = None,
    rating_provider_output: Literal[
        "Fitch", "Moody", "S&P", "Bloomberg", "DBRS"
    ] = "S&P",
    tenor: Literal["long-term", "short-term"] = "long-term",
) -> pd.Series:
    """Consolidate ratings on a security level basis across rating agencies .

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    method
        Defines the method that will be used in order to consolidate the ratings on a
        security level basis across rating agencies.
        Valid methods are {"best", "second_best", "worst"}.
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.

        If None, `rating_provider_input` will be inferred from the dataframe column
        names.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.
    tenor
        Should contain any valid tenor out of {"long-term", "short-term"}

    Returns
    -------
    pd.Series
        Consolidated ratings on a security level basis.

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

    Identify the best ratings:

    >>> consolidate_ratings(
    ...     ratings=ratings_df,
    ...     method="best",
    ...     rating_provider_input=["S&P", "Moody", "Fitch"],
    ...     rating_provider_output="Moody",
    ... )
    0    Aaa
    1    Aa3
    2    Aa1
    3    Ba3
    4    Ca
    Name: best_rtg, dtype: object

    Identify the second-best ratings:

    >>> consolidate_ratings(
    ...     ratings=ratings_df,
    ...     method="second_best",
    ...     rating_provider_input=["S&P", "Moody", "Fitch"],
    ...     rating_provider_output="DBRS",
    ... )
    0    AAH
    1    AAL
    2    AA
    3    BBL
    4    C
    Name: second_best_rtg, dtype: object

    Identify the worst ratings:

    >>> consolidate_ratings(
    ...     ratings=ratings_df,
    ...     method="worst",
    ...     rating_provider_input=["S&P", "Moody", "Fitch"]
    ... )
    0    AA-
    1    AA-
    2    AA-
    3    B+
    4    C
    Name: worst_rtg, dtype: object

    """
    func = {
        "best": get_best_scores,
        "second_best": get_second_best_scores,
        "worst": get_worst_scores,
    }

    # translate ratings -> scores
    rating_scores_series = func[method](
        ratings, rating_provider_input=rating_provider_input, tenor=tenor
    )
    # convert back to ratings
    ratings_series = get_ratings_from_scores(
        rating_scores=rating_scores_series,
        rating_provider=rating_provider_output,
        tenor=tenor,
    )
    ratings_series.name = f"{method}_rtg"
    return ratings_series


def get_best_ratings(
    ratings: pd.DataFrame,
    rating_provider_input: list[str] = None,
    rating_provider_output: Literal[
        "Fitch", "Moody", "S&P", "Bloomberg", "DBRS"
    ] = "S&P",
    tenor: Literal["long-term", "short-term"] = "long-term",
) -> pd.Series:
    """Compute the best rating on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.

        If None, `rating_provider_input` will be inferred from the dataframe column
        names.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.
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
    ratings_series = consolidate_ratings(
        method="best",
        ratings=ratings,
        rating_provider_input=rating_provider_input,
        rating_provider_output=rating_provider_output,
        tenor=tenor,
    )

    return ratings_series


def get_second_best_ratings(
    ratings: pd.DataFrame,
    rating_provider_input: list[str] = None,
    rating_provider_output: Literal[
        "Fitch", "Moody", "S&P", "Bloomberg", "DBRS"
    ] = "S&P",
    tenor: Literal["long-term", "short-term"] = "long-term",
) -> pd.Series:
    """Compute the second-best rating on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.

        If None, `rating_provider_input` will be inferred from the dataframe column
        names.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.
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
    ratings_series = consolidate_ratings(
        method="second_best",
        ratings=ratings,
        rating_provider_input=rating_provider_input,
        rating_provider_output=rating_provider_output,
        tenor=tenor,
    )

    return ratings_series


def get_worst_ratings(
    ratings: pd.DataFrame,
    rating_provider_input: list[str] = None,
    rating_provider_output: Literal[
        "Fitch", "Moody", "S&P", "Bloomberg", "DBRS"
    ] = "S&P",
    tenor: Literal["long-term", "short-term"] = "long-term",
) -> pd.Series:
    """Compute the worst rating on a security level basis across rating agencies.

    Parameters
    ----------
    ratings
        Dataframe consisting of clean ratings (i.e. stripped off of watches/outlooks)
    rating_provider_input
        Indicates rating providers within `ratings`. Should contain any valid rating
        provider out of {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.

        If None, `rating_provider_innput` will be inferred from the dataframe column
        names.
    rating_provider_output
        Indicates which rating scale will be used for output results.
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"}.
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
    ratings_series = consolidate_ratings(
        method="worst",
        ratings=ratings,
        rating_provider_input=rating_provider_input,
        rating_provider_output=rating_provider_output,
        tenor=tenor,
    )

    return ratings_series
