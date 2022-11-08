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

"""Module contains some utility functions."""

import importlib.resources as pkg_resources
import sqlite3
from typing import Dict, Hashable, List, Union

from pyratings import resources

RATINGS_DB = pkg_resources.files(resources).joinpath("Ratings.db")
VALUE_ERROR_PROVIDER_MANDATORY = "'rating_provider' must not be None."
valid_rtg_agncy = {
    "long-term": ["fitch", "moody", "sp", "s&p", "dbrs", "bloomberg", "ice"],
    "short-term": ["fitch", "moody", "sp", "s&p", "dbrs"],
}


def _extract_rating_provider(
    rating_provider: Union[str, List[str], Hashable],
    valid_rtg_provider: list[str],
) -> Union[str, List[str]]:
    """Extract valid rating providers.

    It is meant to extract rating providers from the column headings of a
    ``pd.DataFrame``. For example, let's assume some rating column headers are
    ["rating_fitch", "S&P rating", "BLOOMBERG composite rating"]. The function would
    then return a list of valid rating providers, namely ["Fitch", "SP", "Bloomberg"].

    Parameters
    ----------
    rating_provider
        Should contain any valid rating provider out of
        {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.
    valid_rtg_provider
        List of strings containing the names of valid rating providers. Supported
        rating providers are {"Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"}.
        'rating_provider' must be in that list.

    Returns
    -------
    Union[str, List[str]]
        str or List[str] with valid rating providers.

    Raises
    ------
    AssertionError
        If ``rating_provider`` is not a subset of `valid_rtg_provider`.

    Examples
    --------
    >>> _extract_rating_provider(
    ...     rating_provider="S&P",
    ...     valid_rtg_provider=["fitch", "s&p", "moody"],
    ... )
    'SP'

    >>> _extract_rating_provider(
    ...     rating_provider="rtg_DBRS",
    ...     valid_rtg_provider=["Fitch", "SP", "DBRS"]
    ... )
    'DBRS'

    You can also provide a list of strings.

    >>> _extract_rating_provider(
    ...     rating_provider=["Fitch ratings", "rating_SP", "ICE"],
    ...     valid_rtg_provider=["fitch", "moody", "sp", "bloomberg", "dbrs", "ice"]
    ... )
    ['Fitch', 'SP', 'ICE']

    """
    provider_map = {
        "fitch": "Fitch",
        "moody": "Moody",
        "moody's": "Moody",
        "sp": "SP",
        "s&p": "SP",
        "bloomberg": "Bloomberg",
        "dbrs": "DBRS",
        "ice": "ICE",
    }
    if isinstance(rating_provider, str):
        rating_provider = [rating_provider]

    valid_rtg_provider_lowercase = [x.lower() for x in valid_rtg_provider]

    for i, provider in enumerate(rating_provider):
        if not any(x in provider.lower() for x in valid_rtg_provider_lowercase):
            raise AssertionError(
                f"'{provider}' is not a valid rating provider. 'rating_provider' must "
                f"be in {valid_rtg_provider}."
            )
        for valid_provider in valid_rtg_provider:
            if valid_provider.lower() in provider.lower():
                rating_provider[i] = provider_map[valid_provider.lower()]

    if len(rating_provider) > 1:
        return rating_provider
    else:
        return rating_provider[0]


def _get_translation_dict(
    translation_table: str, rating_provider: str = None, tenor: str = "long-term"
) -> Dict:
    """Load translation dictionaries from SQLite database."""
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
