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

"""Module contains unit tests for functions to get warf from ratings/rating scores."""

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

import pyratings as rtg
from tests import conftest


# --- input: single rating score/rating
@pytest.mark.parametrize(
    "score, warf",
    [
        (1, 1),
        (2, 10),
        (4, 40),
        (5, 70),
        (9, 360),
        (22, 10_000),
    ],
)
def test_get_warf_from_single_rating_score(score: int, warf: int) -> None:
    """It returns a WARF."""
    act = rtg.get_warf_from_scores(rating_scores=score)
    assert act == warf


@pytest.mark.parametrize("score", [-5, 20000])
def test_get_warf_from_invalid_single_rating_score(score: int) -> None:
    """It returns NaN."""
    assert pd.isna(rtg.get_warf_from_scores(rating_scores=score))


@pytest.mark.parametrize(
    ["rating_provider", "rating", "warf"],
    list(
        pd.concat(
            [
                conftest.lt_rtg_df_long,
                conftest.warf_df_long["warf"],
            ],
            axis=1,
        ).to_records(index=False)
    ),
)
def test_get_warf_from_single_rating(
    rating_provider: str, rating: str, warf: int
) -> None:
    """It returns a WARF."""
    act = rtg.get_warf_from_ratings(ratings=rating, rating_provider=rating_provider)

    assert act == warf


def test_get_warf_from_single_rating_invalid_rating_provider() -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_warf_from_ratings(ratings="AA", rating_provider="foo")

    assert str(err.value) == conftest.LT_ERR_MSG


def test_get_warf_with_invalid_single_rating() -> None:
    """It returns NaN."""
    act = rtg.get_warf_from_ratings(ratings="foo", rating_provider="Fitch")
    assert pd.isna(act)


# --- input: ratings series
def test_get_warf_from_rating_scores_series() -> None:
    """It returns a series with WARFs."""
    scores_series = conftest.lt_scores_df_wide.iloc[:, 0]
    warf_series = conftest.warf_df_wide.iloc[:, 0]
    warf_series.name = "warf_Fitch"

    act = rtg.get_warf_from_scores(rating_scores=scores_series)
    assert_series_equal(act, warf_series)


def test_get_warf_from_invalid_rating_scores_series() -> None:
    """It returns a series with NaNs."""
    scores_series = pd.Series(data=[np.nan, "foo", -10], name="rtg_score")
    warf_series = pd.Series(data=[np.nan, np.nan, np.nan], name="warf_rtg_score")

    act = rtg.get_warf_from_scores(rating_scores=scores_series)
    assert_series_equal(act, warf_series)


@pytest.mark.parametrize(
    ["rating_provider", "ratings_series", "warf_series"],
    [
        (
            rating_provider,
            conftest.lt_rtg_df_long.loc[
                conftest.lt_rtg_df_long["rating_provider"] == rating_provider,
                ["rating"],
            ]
            .reset_index(drop=True)
            .squeeze(),
            conftest.warf_df_long.loc[
                conftest.warf_df_long["rating_provider"] == rating_provider,
                "warf",
            ]
            .reset_index(drop=True)
            .squeeze(),
        )
        for rating_provider in conftest.lt_rtg_prov_list
    ],
)
def test_get_warf_from_ratings_series(
    rating_provider: str, ratings_series: pd.Series, warf_series: pd.Series
) -> None:
    """It returns a series with WARFs."""
    act = rtg.get_warf_from_ratings(
        ratings=ratings_series, rating_provider=rating_provider
    )
    warf_series.name = "warf_rating"
    assert_series_equal(act, warf_series)


def test_get_warf_from_ratings_series_invalid_rating_provider() -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_warf_from_ratings(
            ratings=pd.Series(data=["AAA", "AA", "D"], name="foo")
        )

    assert str(err.value) == conftest.LT_ERR_MSG


def test_get_warf_from_invalid_ratings_series() -> None:
    """It returns a series with NaNs."""
    ratings_series = pd.Series(data=[np.nan, "foo", 10], name="Fitch Ratings")
    warf_series = pd.Series(data=[np.nan, np.nan, np.nan], name="warf_Fitch Ratings")

    act = rtg.get_warf_from_ratings(ratings=ratings_series)
    assert_series_equal(act, warf_series)


# --- input: ratings dataframe
exp = conftest.warf_df_wide
exp = pd.concat(
    [
        exp,
        pd.DataFrame(
            data=[[np.nan, np.nan, np.nan, np.nan, np.nan]],
            columns=exp.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)
exp.columns = [
    "warf_Fitch",
    "warf_Moody",
    "warf_SP",
    "warf_Bloomberg",
    "warf_DBRS",
]


def test_get_warf_from_rating_scores_dataframe() -> None:
    """It returns a dataframe with WARFs and NaNs."""
    act = rtg.get_warf_from_scores(
        rating_scores=conftest.lt_scores_df_wide_with_err_row
    )
    assert_frame_equal(act, exp)


def test_get_warf_from_invalid_rating_scores_dataframe() -> None:
    """It returns a dataframe with NaNs."""
    act = rtg.get_warf_from_scores(rating_scores=conftest.input_invalid_df)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["warf_Fitch", "warf_DBRS"]
    assert_frame_equal(act, expectations)


def test_get_warf_from_ratings_dataframe_with_explicit_rating_provider() -> None:
    """It returns a dataframe with WARFs and NaNs."""
    act = rtg.get_warf_from_ratings(
        ratings=conftest.lt_rtg_df_wide_with_err_row,
        rating_provider=["Fitch", "Moody's", "S&P", "Bloomberg", "DBRS"],
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


def test_get_warf_from_ratings_dataframe_by_inferring_rating_provider() -> None:
    """It returns a dataframe with WARFs and NaNs."""
    act = rtg.get_warf_from_ratings(ratings=conftest.lt_rtg_df_wide_with_err_row)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


def test_get_warf_from_ratings_dataframe_invalid_rating_provider() -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_warf_from_ratings(
            ratings=conftest.lt_rtg_df_wide, rating_provider="foo"
        )

    assert str(err.value) == conftest.LT_ERR_MSG


def test_get_warf_from_invalid_ratings_dataframe() -> None:
    """It returns a dataframe with NaNs."""
    act = rtg.get_warf_from_ratings(ratings=conftest.input_invalid_df)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["warf_Fitch", "warf_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations)
