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

"""Module contains unit tests for functions to clean ratings."""

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

import pyratings as rtg
from tests import conftest


def test_get_pure_ratings_single_rating_with_watch() -> None:
    """It returns a single clean rating."""
    assert rtg.get_pure_ratings("AA+ *+") == "AA+"


def test_get_pure_ratings_single_rating_with_unsolicited_lowercase_u() -> None:
    """It returns a single clean rating."""
    assert rtg.get_pure_ratings("AA+u") == "AA+"


def test_get_pure_ratings_single_rating_with_unsolicited_uppercase_u() -> None:
    """It returns a single clean rating."""
    assert rtg.get_pure_ratings("AA+U") == "AA+"


def test_get_pure_ratings_single_rating_with_unsolicited_lowercase_u_watch() -> None:
    """It returns a single clean rating."""
    assert rtg.get_pure_ratings("AA+u (CWNegative)") == "AA+"


def test_get_pure_ratings_single_rating_with_unsolicited_uppercase_u_watch() -> None:
    """It returns a single clean rating."""
    assert rtg.get_pure_ratings("AA+U *-") == "AA+"


def test_get_pure_ratings_single_rating_with_public_information_lowercase_p() -> None:
    """It returns a single clean rating."""
    assert rtg.get_pure_ratings("(p)P-2") == "P-2"


def test_get_pure_ratings_single_rating_with_public_information_uppercase_p() -> None:
    """It returns a single clean rating."""
    assert rtg.get_pure_ratings("(P)P-2") == "P-2"


# --- input: ratings series
@pytest.mark.parametrize(
    ["rating_provider", "rating_series", "rating_series_clean"],
    [
        (
            rating_provider,
            conftest.lt_rtg_df_long_with_watch_unsolicited.loc[
                conftest.lt_rtg_df_long_with_watch_unsolicited["rating_provider"]
                == rating_provider,
                ["rating"],
            ]
            .reset_index(drop=True)
            .squeeze(),
            conftest.lt_rtg_df_long.loc[
                conftest.lt_rtg_df_long["rating_provider"] == rating_provider,
                ["rating"],
            ]
            .reset_index(drop=True)
            .squeeze(),
        )
        for rating_provider in conftest.lt_rtg_prov_list
    ],
)
def test_get_pure_ratings_series(
    rating_provider: str, rating_series: pd.Series, rating_series_clean: pd.Series
) -> None:
    """It returns a series with clean ratings."""
    rating_series_clean.name = "rating_clean"
    act = rtg.get_pure_ratings(rating_series)

    assert_series_equal(act, rating_series_clean)


def test_get_pure_ratings_series_with_nan() -> None:
    """It returns the unchanged input series, i.e. no cleaning at all."""
    series = conftest.input_invalid_df.iloc[:, 0].copy()
    series.name = "Fitch_clean"

    assert_series_equal(rtg.get_pure_ratings(series), series)


def test_get_pure_ratings_df() -> None:
    """It returns a dataframe with clean ratigns."""
    act = rtg.get_pure_ratings(conftest.lt_rtg_df_wide_with_watch_unsolicited)
    exp = conftest.lt_rtg_df_wide.copy()
    exp = exp.add_suffix("_clean")

    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


def test_get_pure_ratings_df_with_nan() -> None:
    """It returns the unchanged input dataframe, i.e. no cleaning at all."""
    act = rtg.get_pure_ratings(conftest.input_invalid_df)
    exp = conftest.input_invalid_df.copy()
    exp.columns = ["Fitch_clean", "DBRS_clean"]

    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)
