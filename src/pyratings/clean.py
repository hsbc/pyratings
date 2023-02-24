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

"""Module contains functions to clean ratings."""

from __future__ import annotations  # required for Python < 3.10

import pandas as pd


def get_pure_ratings(
    ratings: str | pd.Series | pd.DataFrame,
) -> str | pd.Series | pd.DataFrame:
    """Remove rating watches/outlooks and other non-actual-rating related information.

    Ratings may contain watch, such as 'AA- *+', 'BBB+ (CwNegative)'.
    Outlook/watch should be seperated by a blank from the actual rating.
    Also, ratings may also contain the letter 'u' (unsolicited) or be prefixed by
    '(P)' (public information only).
    This kind of information will be removed to retrieve the actual rating(s).

    Parameters
    ----------
    ratings
        Uncleaned rating(s).

    Returns
    -------
    Union[str, pd.Series, pd.DataFrame]
        Regular ratings stripped off of watches. The name of the resulting Series or
        the columns of the returning DataFrame will be suffixed with `_clean`.

    Examples
    --------
    Cleaning a single rating:

    >>> get_pure_ratings("AA- *+")
    'AA-'

    >>> get_pure_ratings("Au")
    'A'

    >>> get_pure_ratings("(P)P-2")
    'P-2'

    Cleaning a `pd.Series`:

    >>> import numpy as np
    >>> import pandas as pd

    >>> rating_series=pd.Series(
    ...    data=[
    ...        "BB+ *-",
    ...        "(P)BBB *+",
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
        ratings = (
            ratings.split()[0].rstrip("uU").removeprefix("(p)").removeprefix("(P)")
        )
        return ratings

    elif isinstance(ratings, pd.Series):
        # identify string occurrences
        isstring = ratings.apply(type).eq(str)

        # strip string after occurrence of very first blank and strip character 'u',
        # which has usually been added without a blank;
        # also remove suffix '(p)' and '(P)'
        ratings[isstring] = ratings[isstring].str.split().str[0]
        ratings[isstring] = ratings[isstring].str.rstrip("uU")
        ratings[isstring] = ratings[isstring].str.removeprefix("(p)")
        ratings[isstring] = ratings[isstring].str.removeprefix("(P)")
        ratings.name = f"{ratings.name}_clean"
        return ratings

    elif isinstance(ratings, pd.DataFrame):
        # Recursive call of `get_pure_ratings`
        return pd.concat(
            [get_pure_ratings(ratings=ratings[col]) for col in ratings.columns], axis=1
        )
