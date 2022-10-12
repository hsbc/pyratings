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

"""Module contains functions to translate ratings / rating scores into WARF."""

from typing import List, Optional, Union

import numpy as np
import pandas as pd

from pyratings.get_scores import get_scores_from_ratings
from pyratings.utils import _extract_rating_provider, _get_translation_dict


def get_warf_from_scores(
    rating_scores: Union[int, float, pd.Series, pd.DataFrame],
) -> Union[int, pd.Series, pd.DataFrame]:
    """Convert numerical rating scores to numerical WARFs.

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
    """Convert regular ratings to numerical WARFs.

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
            rating_scores.columns = rating_scores.columns.str.removeprefix("rtg_score_")
        except AttributeError:
            pass
        return get_warf_from_scores(rating_scores=rating_scores)
