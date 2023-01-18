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

"""Module contains unit tests for functions to get scores from ratings/warf."""

from typing import Union

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

import pyratings as rtg
from tests import conftest


# --- input: single rating/warf
@pytest.mark.parametrize(
    ["rating_provider", "rating", "score"],
    list(
        pd.concat(
            [
                conftest.lt_rtg_df_long,
                conftest.lt_scores_df_long["rtg_score"],
            ],
            axis=1,
        ).to_records(index=False)
    ),
)
def test_get_scores_from_single_rating_longterm(
    rating_provider: str, rating: str, score: int
) -> None:
    """It returns a rating score."""
    act = rtg.get_scores_from_ratings(
        ratings=rating, rating_provider=rating_provider, tenor="long-term"
    )

    assert act == score


@pytest.mark.parametrize(
    ["rating_provider", "rating", "score"],
    conftest.st_basestrat_prov_rtg_scrs_records,
)
def test_get_scores_from_single_rating_shortterm(
    rating_provider: str, rating: str, score: int
) -> None:
    """It returns a rating score."""
    act = rtg.get_scores_from_ratings(
        ratings=rating,
        rating_provider=rating_provider,
        tenor="short-term",
    )

    assert act == score


def test_get_scores_from_single_rating_shortterm_without_specifying_strategy() -> None:
    """It returns a human-readable short-term rating."""
    act = rtg.get_scores_from_ratings(
        ratings="P-1",
        rating_provider="Moody",
        tenor="short-term",
    )

    assert act == 3.5


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_single_rating_invalid_rating_provider(tenor: str) -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_scores_from_ratings(ratings="AA", rating_provider="foo", tenor=tenor)

    if tenor == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_with_invalid_single_rating(tenor: str) -> None:
    """It returns NaN."""
    act = rtg.get_scores_from_ratings(
        ratings="foo", rating_provider="Fitch", tenor=tenor
    )
    assert pd.isna(act)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_with_single_rating_and_no_rating_provider(tenor: str) -> None:
    """It raises an error message."""
    with pytest.raises(ValueError) as err:
        rtg.get_scores_from_ratings(ratings="BBB", tenor=tenor)

    assert str(err.value) == "'rating_provider' must not be None."


@pytest.mark.parametrize(
    "warf, score",
    [
        (1, 1),
        (6, 2),
        (54.9999, 4),
        (55, 5),
        (55.00001, 5),
        (400, 9),
        (10_000, 22),
    ],
)
def test_get_scores_from_single_warf(warf: int, score: int) -> None:
    """It returns a rating score."""
    act = rtg.get_scores_from_warf(warf=warf)
    assert act == score


@pytest.mark.parametrize("warf", [np.nan, -5, 20000.5])
def test_get_scores_from_invalid_single_warf(warf: Union[int, float]) -> None:
    """It returns NaN."""
    assert pd.isna(rtg.get_scores_from_warf(warf=warf))


# --- input: ratings series
@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.lt_prov_scrs_rtg,
)
def test_get_scores_from_ratings_series_longterm(
    rating_provider: str, ratings_series: pd.Series, scores_series: pd.Series
) -> None:
    """It returns a series with rating scores."""
    scores_series.name = f"rtg_score_{ratings_series.name}"
    act = rtg.get_scores_from_ratings(
        ratings=ratings_series, rating_provider=rating_provider
    )
    assert_series_equal(act, scores_series)


@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.st_basestrat_prov_scores_rtg_series,
)
def test_get_scores_from_ratings_series_shortterm(
    rating_provider: str,
    ratings_series: pd.Series,
    scores_series: pd.Series,
) -> None:
    """It returns a series with rating scores."""
    scores_series.name = f"rtg_score_{ratings_series.name}"
    act = rtg.get_scores_from_ratings(
        ratings=ratings_series,
        rating_provider=rating_provider,
        tenor="short-term",
    )
    assert_series_equal(act, scores_series)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_ratings_series_invalid_rating_provider(tenor: str) -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_scores_from_ratings(
            ratings=pd.Series(data=["AAA", "AA", "D"], name="rating"),
            rating_provider="foo",
            tenor=tenor,
        )

    if tenor == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_invalid_ratings_series(tenor: str) -> None:
    """It returns a series with NaNs."""
    ratings_series = pd.Series(data=[np.nan, "foo", -10], name="rating")
    scores_series = pd.Series(data=[np.nan, np.nan, np.nan], name="rtg_score_rating")

    act = rtg.get_scores_from_ratings(
        ratings=ratings_series, rating_provider="Fitch", tenor=tenor
    )
    assert_series_equal(act, scores_series)


def test_get_scores_from_warf_series() -> None:
    """It returns a series with rating scores."""
    warf_series = conftest.warf_df_wide.iloc[:, 0]
    scores_series = conftest.lt_scores_df_wide.iloc[:, 0]
    scores_series.name = "rtg_score"

    act = rtg.get_scores_from_warf(warf=warf_series)
    assert_series_equal(act, scores_series)


def test_get_scores_from_invalid_warf_series() -> None:
    """It returns a series with NaNs."""
    warf_series = pd.Series(data=[np.nan, "foo", -10], name="warf")
    scores_series = pd.Series(data=[np.nan, np.nan, np.nan], name="rtg_score")

    act = rtg.get_scores_from_warf(warf=warf_series)
    assert_series_equal(act, scores_series)


# --- input: ratings dataframe
exp_lt = conftest.lt_scores_df_wide
exp_lt = pd.concat(
    [
        exp_lt,
        pd.DataFrame(
            data=[[np.nan, np.nan, np.nan, np.nan, np.nan]],
            columns=exp_lt.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)
exp_lt.columns = [
    "rtg_score_Fitch",
    "rtg_score_Moody",
    "rtg_score_SP",
    "rtg_score_Bloomberg",
    "rtg_score_DBRS",
]


def test_get_scores_from_ratings_df_with_explicit_rating_provider_longterm() -> None:
    """It returns a dataframe with rating scores and NaNs."""
    act = rtg.get_scores_from_ratings(
        ratings=conftest.lt_rtg_df_wide_with_err_row,
        rating_provider=[
            "rtg_Fitch",
            "Moody's rating",
            "Rating S&P",
            "Bloomberg Bloomberg RATING",
            "DBRS",
        ],
        tenor="long-term",
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


def test_get_scores_from_ratings_df_with_explicit_rating_provider_shortterm() -> None:
    """It returns a dataframe with rating scores and NaNs."""
    input_df = (
        conftest.st_rtg_df_wide.loc[conftest.st_rtg_df_wide["Strategy"] == "base"]
        .iloc[:, 1:]
        .reset_index(drop=True)
    )
    act = rtg.get_scores_from_ratings(
        ratings=input_df,
        rating_provider=[
            "rtg_Fitch",
            "Moody's rating",
            "Rating S&P",
            "DBRS",
        ],
        tenor="short-term",
    )
    exp = (
        conftest.st_scores_df_wide.loc[conftest.st_scores_df_wide["Strategy"] == "base"]
        .iloc[:, 1:]
        .reset_index(drop=True)
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


def test_get_scores_from_ratings_df_by_inferring_rating_provider_longterm() -> None:
    """It returns a dataframe with rating scores and NaNs."""
    act = rtg.get_scores_from_ratings(
        ratings=conftest.lt_rtg_df_wide_with_err_row, tenor="long-term"
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


def test_get_scores_from_ratings_df_by_inferring_rating_provider_shortterm() -> None:
    """It returns a dataframe with rating scores and NaNs."""
    input_df = (
        conftest.st_rtg_df_wide.loc[conftest.st_rtg_df_wide["Strategy"] == "base"]
        .iloc[:, 1:]
        .reset_index(drop=True)
    )
    act = rtg.get_scores_from_ratings(ratings=input_df, tenor="short-term")
    exp = (
        conftest.st_scores_df_wide.loc[conftest.st_scores_df_wide["Strategy"] == "base"]
        .iloc[:, 1:]
        .reset_index(drop=True)
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_ratings_df_invalid_rating_provider(tenor: str) -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_scores_from_ratings(
            ratings=conftest.lt_rtg_df_wide, rating_provider="foo", tenor=tenor
        )

    if tenor == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_invalid_ratings_df(tenor: str) -> None:
    """It returns a dataframe with NaNs."""
    act = rtg.get_scores_from_ratings(ratings=conftest.input_invalid_df, tenor=tenor)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["rtg_score_Fitch", "rtg_score_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations)


def test_get_scores_from_warf_df() -> None:
    """It returns a dataframe with rating scores and NaNs."""
    act = rtg.get_scores_from_warf(warf=conftest.warf_df_wide_with_err_row)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


def test_get_scores_from_invalid_warf_df() -> None:
    """It returns a dataframe with NaNs."""
    act = rtg.get_scores_from_warf(warf=conftest.input_invalid_df)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["rtg_score_Fitch", "rtg_score_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations)
