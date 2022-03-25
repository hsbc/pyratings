"""
Copyright 2022 HSBC Global Asset Management (Deutschland) GmbH

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
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
                conftest.rtg_df_long,
                conftest.scores_df_long["rtg_score"],
            ],
            axis=1,
        ).to_records(index=False)
    ),
)
def test_get_scores_from_single_rating_longterm(rating_provider, rating, score):
    """Tests if function can handle single string objects."""
    act = rtg.get_scores_from_ratings(
        ratings=rating, rating_provider=rating_provider, tenor="long-term"
    )

    assert act == score


@pytest.mark.parametrize(
    ["rating_provider", "rating", "score"],
    list(
        pd.concat(
            [
                conftest.rtg_df_long_st,
                conftest.scores_df_long_st["rtg_score"],
            ],
            axis=1,
        ).to_records(index=False)
    ),
)
def test_get_scores_from_single_rating_shortterm(rating_provider, rating, score):
    """Tests if function can handle single string objects."""
    act = rtg.get_scores_from_ratings(
        ratings=rating, rating_provider=rating_provider, tenor="short-term"
    )

    assert act == score


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_single_rating_invalid_rating_provider(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_scores_from_ratings(ratings="AA", rating_provider="foo", tenor=tenor)

    assert str(err.value) == conftest.ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_with_invalid_single_rating(tenor):
    """Tests if function returns NaN for invalid inputs."""
    act = rtg.get_scores_from_ratings(
        ratings="foo", rating_provider="Fitch", tenor=tenor
    )
    assert pd.isna(act)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_with_single_rating_and_no_rating_provider(tenor):
    """Tests if correct error message will be raised."""
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
def test_get_scores_from_single_warf(warf, score):
    """Tests if function can correctly handle individual warf (float)."""
    act = rtg.get_scores_from_warf(warf=warf)
    assert act == score


@pytest.mark.parametrize("warf", [np.nan, -5, 20000.5])
def test_get_scores_from_invalid_single_warf(warf):
    """Tests if function returns NaN for invalid inputs."""
    assert pd.isna(rtg.get_scores_from_warf(warf=warf))


# --- input: ratings series
@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.params_provider_scores_ratings_lt,
)
def test_get_scores_from_ratings_series_longterm(
    rating_provider, ratings_series, scores_series
):
    """Tests if function can correctly handle pd.Series objects."""
    scores_series.name = f"rtg_score_{rating_provider}"
    act = rtg.get_scores_from_ratings(
        ratings=ratings_series, rating_provider=rating_provider
    )
    assert_series_equal(act, scores_series)


@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.params_provider_scores_ratings_st,
)
def test_get_scores_from_ratings_series_shortterm(
    rating_provider, ratings_series, scores_series
):
    """Tests if function can correctly handle pd.Series objects."""
    scores_series.name = f"rtg_score_{rating_provider}"
    act = rtg.get_scores_from_ratings(
        ratings=ratings_series, rating_provider=rating_provider, tenor="short-term"
    )
    assert_series_equal(act, scores_series)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_ratings_series_invalid_rating_provider(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_scores_from_ratings(
            ratings=pd.Series(data=["AAA", "AA", "D"], name="rating"),
            rating_provider="foo",
            tenor=tenor,
        )

    assert str(err.value) == conftest.ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_invalid_ratings_series(tenor):
    """Tests if function can correctly handle pd.Series objects."""
    ratings_series = pd.Series(data=[np.nan, "foo", -10], name="rating")
    scores_series = pd.Series(data=[np.nan, np.nan, np.nan], name="rtg_score_Fitch")

    act = rtg.get_scores_from_ratings(
        ratings=ratings_series, rating_provider="Fitch", tenor=tenor
    )
    assert_series_equal(act, scores_series)


def test_get_scores_from_warf_series():
    """Tests if function can correctly handle pd.Series objects."""
    warf_series = conftest.warf_df_wide.iloc[:, 0]
    scores_series = conftest.scores_df_wide.iloc[:, 0]
    scores_series.name = "rtg_score"

    act = rtg.get_scores_from_warf(warf=warf_series)
    assert_series_equal(act, scores_series)


def test_get_scores_from_invalid_warf_series():
    """Tests if function can correctly handle pd.Series objects."""
    warf_series = pd.Series(data=[np.nan, "foo", -10], name="warf")
    scores_series = pd.Series(data=[np.nan, np.nan, np.nan], name="rtg_score")

    act = rtg.get_scores_from_warf(warf=warf_series)
    assert_series_equal(act, scores_series)


# --- input: ratings dataframe
exp_lt = conftest.scores_df_wide
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
    "rtg_score_Fitch",
    "rtg_score_Moody",
    "rtg_score_SP",
    "rtg_score_Bloomberg",
    "rtg_score_DBRS",
    "rtg_score_ICE",
]

exp_st = conftest.scores_df_wide_st
exp_st = pd.concat(
    [
        exp_st,
        pd.DataFrame(data=[[np.nan, np.nan, np.nan, np.nan]], columns=exp_st.columns),
    ],
    axis=0,
    ignore_index=True,
)
exp_st.columns = [
    "rtg_score_Fitch",
    "rtg_score_Moody",
    "rtg_score_SP",
    "rtg_score_DBRS",
]


def test_get_scores_from_ratings_dataframe_with_explicit_rating_provider_longterm():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_scores_from_ratings(
        ratings=conftest.rtg_df_wide_with_err_row,
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


def test_get_scores_from_ratings_dataframe_with_explicit_rating_provider_shortterm():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_scores_from_ratings(
        ratings=conftest.rtg_df_wide_st_with_err_row,
        rating_provider=[
            "rtg_Fitch",
            "Moody's rating",
            "Rating S&P",
            "DBRS",
        ],
        tenor="short-term",
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_st)


def test_get_scores_from_ratings_dataframe_by_inferring_rating_provider_longterm():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_scores_from_ratings(
        ratings=conftest.rtg_df_wide_with_err_row, tenor="long-term"
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


def test_get_scores_from_ratings_dataframe_by_inferring_rating_provider_shortterm():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_scores_from_ratings(
        ratings=conftest.rtg_df_wide_st_with_err_row, tenor="short-term"
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_st)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_ratings_dataframe_invalid_rating_provider(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_scores_from_ratings(
            ratings=conftest.rtg_df_wide, rating_provider="foo", tenor=tenor
        )

    assert str(err.value) == conftest.ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_scores_from_invalid_ratings_dataframe(tenor):
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_scores_from_ratings(ratings=conftest.input_invalid_df, tenor=tenor)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["rtg_score_Fitch", "rtg_score_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations)


def test_get_scores_from_warf_dataframe():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_scores_from_warf(warf=conftest.warf_df_wide_with_err_row)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


def test_get_scores_from_invalid_warf_dataframe():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_scores_from_warf(warf=conftest.input_invalid_df)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["rtg_score_Fitch", "rtg_score_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations)
