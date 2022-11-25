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

"""Module contains unit tests for functions to get ratings from scores/warf."""

from typing import Union

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

import pyratings as rtg
from tests import conftest


# --- input: single score/warf
@pytest.mark.parametrize(
    ["rating_provider", "score", "rating"],
    list(
        pd.concat(
            [
                conftest.lt_scores_df_long,
                conftest.lt_rtg_df_long["rating"],
            ],
            axis=1,
        ).to_records(index=False)
    ),
)
def test_get_rating_from_single_score_longterm(
    rating_provider: str, score: int, rating: str
) -> None:
    """It returns a human-readable long-term rating."""
    act = rtg.get_ratings_from_scores(
        rating_scores=score, rating_provider=rating_provider, tenor="long-term"
    )

    assert act == rating


def test_get_rating_from_single_score_float_longterm() -> None:
    """It returns a human-readable long-term rating."""
    assert (
        rtg.get_ratings_from_scores(
            rating_scores=5.499, rating_provider="Fitch", tenor="long-term"
        )
        == "A+"
    )
    assert (
        rtg.get_ratings_from_scores(
            rating_scores=5.501, rating_provider="Fitch", tenor="long-term"
        )
        == "A"
    )


@pytest.mark.parametrize(
    ["strategy", "rating_provider", "rating", "score"],
    conftest.st_strat_prov_rtg_scrs_records,
)
def test_get_rating_from_single_score_shortterm(
    strategy: str, rating_provider: str, score: int, rating: str
) -> None:
    """It returns a human-readable short-term rating."""
    act = rtg.get_ratings_from_scores(
        rating_scores=score,
        rating_provider=rating_provider,
        tenor="short-term",
        short_term_strategy=strategy,
    )

    assert act == rating


def test_get_rating_from_single_score_shortterm_without_specifying_strategy() -> None:
    """It returns a human-readable short-term rating."""
    act = rtg.get_ratings_from_scores(
        rating_scores=5,
        rating_provider="Moody",
        tenor="short-term",
    )

    assert act == "P-1"


def test_get_rating_from_single_score_float_shortterm() -> None:
    """It returns a human-readable short-term rating."""
    assert (
        rtg.get_ratings_from_scores(
            rating_scores=4.499, rating_provider="DBRS", tenor="short-term"
        )
        == "R-1 M"
    )
    assert (
        rtg.get_ratings_from_scores(
            rating_scores=4.501, rating_provider="DBRS", tenor="short-term"
        )
        == "R-1 L"
    )


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_single_score_invalid_rating_provider(tenor: str) -> None:
    """It returns an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=10, rating_provider="foo", tenor=tenor
        )
    if tenor == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_with_invalid_single_score(tenor: str) -> None:
    """It returns NaN."""
    act = rtg.get_ratings_from_scores(
        rating_scores=-5, rating_provider="Fitch", tenor=tenor
    )
    assert pd.isna(act)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_with_single_score_and_no_rating_provider(tenor: str) -> None:
    """It raises an error message."""
    with pytest.raises(ValueError) as err:
        rtg.get_ratings_from_scores(rating_scores=-5, tenor=tenor)

    assert str(err.value) == "'rating_provider' must not be None."


@pytest.mark.parametrize(
    "warf, rating_provider, rating",
    [
        (1, "SP", "AAA"),
        (455, "SP", "BBB"),
        (484.9999, "SP", "BBB"),
        (485, "Moody", "Baa3"),
        (9999, "Moody's", "C"),
        (10000, "Fitch", "D"),
    ],
)
def test_get_ratings_from_single_warf(
    warf: Union[int, float], rating_provider: str, rating: str
) -> None:
    """It returns a human-readable rating."""
    act = rtg.get_ratings_from_warf(warf=warf, rating_provider=rating_provider)
    assert act == rating


def test_get_ratings_from_single_warf_with_no_rating_provider() -> None:
    """It raises an error message."""
    with pytest.raises(ValueError) as err:
        rtg.get_ratings_from_warf(warf=100, rating_provider=None)

    assert str(err.value) == "'rating_provider' must not be None."


@pytest.mark.parametrize("warf", [np.nan, -5, 20000])
def test_get_ratings_from_invalid_single_warf(warf: Union[int, float]) -> None:
    """It returns NaN."""
    assert pd.isna(rtg.get_ratings_from_warf(warf=warf, rating_provider="DBRS"))


# --- input: ratings score series
@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.lt_prov_scrs_rtg,
)
def test_get_ratings_from_scores_series_longterm(
    rating_provider: str, scores_series: pd.Series, ratings_series: pd.Series
) -> None:
    """It returns a series with human-readable long-term ratings."""
    act = rtg.get_ratings_from_scores(
        rating_scores=scores_series, rating_provider=rating_provider
    )
    ratings_series.name = f"rtg_{rating_provider}"
    assert_series_equal(act, ratings_series)


@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.lt_prov_scrs_rtg,
)
def test_get_ratings_from_scores_series_longterm_float(
    rating_provider: str, scores_series: pd.Series, ratings_series: pd.Series
) -> None:
    """It returns a series with human-readable long-term ratings."""
    act = rtg.get_ratings_from_scores(
        rating_scores=scores_series.add(0.23), rating_provider=rating_provider
    )
    ratings_series.name = f"rtg_{rating_provider}"
    assert_series_equal(act, ratings_series)


@pytest.mark.parametrize(
    ["strategy", "rating_provider", "scores_series", "ratings_series"],
    conftest.st_strat_prov_scores_rtg_series,
)
def test_get_ratings_from_scores_series_shortterm(
    strategy: str,
    rating_provider: str,
    scores_series: pd.Series,
    ratings_series: pd.Series,
) -> None:
    """It returns a series with human-readable short-term ratings."""
    act = rtg.get_ratings_from_scores(
        rating_scores=scores_series,
        rating_provider=rating_provider,
        tenor="short-term",
        short_term_strategy=strategy,
    )
    ratings_series.name = f"rtg_{rating_provider}"
    assert_series_equal(act, ratings_series)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_scores_series_invalid_rating_provider(tenor: str) -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=pd.Series(data=[1, 3, 22], name="rtg_score"),
            rating_provider="foo",
            tenor=tenor,
        )

    if tenor == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_scores_series_with_no_rating_provider(tenor: str) -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=pd.Series(data=[1, 3, 22], name="foo"),
            tenor=tenor,
        )

    if tenor == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_invalid_scores_series(tenor: str) -> None:
    """It returns a series with NaNs."""
    scores_series = pd.Series(data=[np.nan, "foo", -10], name="rtg_score")
    ratings_series = pd.Series(data=[np.nan, np.nan, np.nan], name="rating")

    act = rtg.get_ratings_from_scores(
        rating_scores=scores_series, rating_provider="Fitch", tenor=tenor
    )
    ratings_series.name = "rtg_Fitch"
    assert_series_equal(act, ratings_series, check_dtype=False)


@pytest.mark.parametrize(
    ["rating_provider", "warf_series", "ratings_series"],
    [
        (
            rating_provider,
            conftest.warf_df_long.loc[
                conftest.lt_scores_df_long["rating_provider"] == rating_provider,
                "warf",
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
def test_get_ratings_from_warf_series(
    rating_provider: str, warf_series: pd.Series, ratings_series: pd.Series
) -> None:
    """It returns a series with human-readable long-term ratings."""
    act = rtg.get_ratings_from_warf(warf=warf_series, rating_provider=rating_provider)
    ratings_series.name = f"rtg_{rating_provider}"
    assert_series_equal(act, ratings_series)


def test_get_ratings_from_invalid_warf_series() -> None:
    """It returns a series with NaNs."""
    warf_series = pd.Series(data=[np.nan, "foo", -10], name="rtg_score")
    ratings_series = pd.Series(data=[np.nan, np.nan, np.nan], name="rating")

    act = rtg.get_ratings_from_warf(warf=warf_series, rating_provider="Fitch")
    ratings_series.name = "rtg_Fitch"
    assert_series_equal(act, ratings_series, check_dtype=False)


# --- input: rating score dataframe
exp_lt = conftest.lt_rtg_df_wide
exp_lt = pd.concat(
    [
        exp_lt,
        pd.DataFrame(
            data=[[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]],
            columns=exp_lt.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)
exp_lt.columns = [
    "rtg_Fitch",
    "rtg_Moody",
    "rtg_SP",
    "rtg_Bloomberg",
    "rtg_DBRS",
    "rtg_ICE",
]


def test_get_ratings_from_scores_df_with_explicit_rating_provider_longterm() -> None:
    """It returns a dataframe with human-readable long-term ratings and NaNs."""
    act = rtg.get_ratings_from_scores(
        rating_scores=conftest.lt_scores_df_wide_with_err_row,
        rating_provider=[
            "rtg_Fitch",
            "Moody's rating",
            "Rating S&P",
            "Bloomberg Bloomberg RATING",
            "DBRS",
            "ICE",
        ],
        tenor="long-term",
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


@pytest.mark.parametrize("strategy", conftest.st_strategies)
def test_get_ratings_from_scores_df_with_explicit_rating_provider_shortterm(
    strategy: str,
) -> None:
    """It returns a dataframe with human-readable short-term ratings and NaNs."""
    input_df = (
        conftest.st_scores_df_wide.loc[
            conftest.st_scores_df_wide["Strategy"] == strategy
        ]
        .iloc[:, 1:]
        .reset_index(drop=True)
    )
    act = rtg.get_ratings_from_scores(
        rating_scores=input_df,
        rating_provider=[
            "rtg_Fitch",
            "Moody's rating",
            "Rating S&P",
            "DBRS",
        ],
        tenor="short-term",
        short_term_strategy=strategy,
    )
    exp = (
        conftest.st_rtg_df_wide.loc[conftest.st_rtg_df_wide["Strategy"] == strategy]
        .iloc[:, 1:]
        .reset_index(drop=True)
    )
    exp = exp.set_axis(["rtg_Fitch", "rtg_Moody", "rtg_SP", "rtg_DBRS"], axis=1)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


def test_get_ratings_from_scores_df_by_inferring_rating_provider_longterm() -> None:
    """It returns a dataframe with human-readable long-term ratings and NaNs."""
    act = rtg.get_ratings_from_scores(
        rating_scores=conftest.lt_scores_df_wide_with_err_row
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


@pytest.mark.parametrize("strategy", conftest.st_strategies)
def test_get_ratings_from_scores_df_by_inferring_rating_provider_shortterm(
    strategy: str,
) -> None:
    """It returns a dataframe with human-readable short-term ratings and NaNs."""
    input_df = (
        conftest.st_scores_df_wide.loc[
            conftest.st_scores_df_wide["Strategy"] == strategy
        ]
        .iloc[:, 1:]
        .reset_index(drop=True)
    )
    act = rtg.get_ratings_from_scores(
        rating_scores=input_df,
        tenor="short-term",
        short_term_strategy=strategy,
    )
    exp = (
        conftest.st_rtg_df_wide.loc[conftest.st_rtg_df_wide["Strategy"] == strategy]
        .iloc[:, 1:]
        .reset_index(drop=True)
    )
    exp = exp.set_axis(["rtg_Fitch", "rtg_Moody", "rtg_SP", "rtg_DBRS"], axis=1)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


def test_get_ratings_from_scores_df_by_inferring_rating_provider_lt_float() -> None:
    """It returns a dataframe with human-readable long-ter ratings and NaNs."""
    scores_df_wide_float = conftest.lt_scores_df_wide + 0.23
    scores_df_wide_float = pd.concat(
        [
            scores_df_wide_float,
            pd.DataFrame(
                data=[["foo", "foo", "foo", "foo", "foo", "foo"]],
                columns=scores_df_wide_float.columns,
            ),
        ],
        axis=0,
        ignore_index=True,
    )
    act = rtg.get_ratings_from_scores(rating_scores=scores_df_wide_float)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_scores_df_invalid_rating_provider(tenor: str) -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=conftest.lt_scores_df_wide, rating_provider="foo", tenor=tenor
        )
    if tenor == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_invalid_rating_scores_df(tenor: str) -> None:
    """It returns a dataframe with NaNs."""
    act = rtg.get_ratings_from_scores(
        rating_scores=conftest.input_invalid_df, tenor=tenor
    )
    expectations = conftest.exp_invalid_df
    expectations.columns = ["rtg_Fitch", "rtg_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations, check_dtype=False)


def test_get_ratings_from_warf_df() -> None:
    """It returns a dataframe with human-readable long-term ratings and NaNs."""
    act = rtg.get_ratings_from_warf(warf=conftest.warf_df_wide_with_err_row)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


def test_get_ratings_from_invalid_warf_df() -> None:
    """It returns a dataframe with NaNs."""
    act = rtg.get_ratings_from_warf(warf=conftest.input_invalid_df)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["rtg_Fitch", "rtg_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations, check_dtype=False)


def test_invalid_short_term_strategy() -> None:
    """It raises an error message."""
    with pytest.raises(ValueError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=5,
            rating_provider="Moody",
            tenor="short-term",
            short_term_strategy="foo",
        )

    assert str(err.value) == (
        "Invalid short_term_strategy. Must be in ['best', 'base', 'worst']."
    )
