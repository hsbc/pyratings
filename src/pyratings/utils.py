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

import importlib.resources as pkg_resources
import sqlite3
from typing import Dict, Hashable, List, Union

from pyratings import resources

RATINGS_DB = pkg_resources.files(resources).joinpath("Ratings.db")
VALUE_ERROR_PROVIDER_MANDATORY = "'rating_provider' must not be None."


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
