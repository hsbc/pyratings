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
def test_get_warf_from_single_rating_score(score, warf):
    """Tests if function can correctly handle individual warf (float)."""
    act = rtg.get_warf_from_scores(rating_scores=score)
    assert act == warf


@pytest.mark.parametrize("score", [-5, 20000])
def test_get_warf_from_invalid_single_rating_score(score):
    """Tests if function returns NaN for invalid inputs."""
    assert pd.isna(rtg.get_warf_from_scores(rating_scores=score))


@pytest.mark.parametrize(
    ["rating_provider", "rating", "warf"],
    list(
        pd.concat(
            [
                conftest.rtg_df_long,
                conftest.warf_df_long["warf"],
            ],
            axis=1,
        ).to_records(index=False)
    ),
)
def test_get_warf_from_single_rating(rating_provider, rating, warf):
    """Tests if function can handle single string objects."""
    act = rtg.get_warf_from_ratings(ratings=rating, rating_provider=rating_provider)

    assert act == warf


def test_get_warf_from_single_rating_invalid_rating_provider():
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_warf_from_ratings(ratings="AA", rating_provider="foo")

    assert str(err.value) == conftest.ERR_MSG


def test_get_warf_with_invalid_single_rating():
    """Tests if function returns NaN for invalid inputs."""
    act = rtg.get_warf_from_ratings(ratings="foo", rating_provider="Fitch")
    assert pd.isna(act)


# --- input: ratings series
def test_get_warf_from_rating_scores_series():
    """Tests if function can correctly handle pd.Series objects."""
    scores_series = conftest.scores_df_wide.iloc[:, 0]
    warf_series = conftest.warf_df_wide.iloc[:, 0]
    warf_series.name = "warf"

    act = rtg.get_warf_from_scores(rating_scores=scores_series)
    assert_series_equal(act, warf_series)


def test_get_warf_from_invalid_rating_scores_series():
    """Tests if function can correctly handle pd.Series objects."""
    scores_series = pd.Series(data=[np.nan, "foo", -10], name="rtg_score")
    warf_series = pd.Series(data=[np.nan, np.nan, np.nan], name="warf")

    act = rtg.get_warf_from_scores(rating_scores=scores_series)
    assert_series_equal(act, warf_series)


@pytest.mark.parametrize(
    ["rating_provider", "ratings_series", "warf_series"],
    conftest.params_provider_ratings_warf,
)
def test_get_warf_from_ratings_series(rating_provider, ratings_series, warf_series):
    """Tests if function can correctly handle pd.Series objects."""
    act = rtg.get_warf_from_ratings(
        ratings=ratings_series, rating_provider=rating_provider
    )
    assert_series_equal(act, warf_series)


def test_get_warf_from_ratings_series_invalid_rating_provider():
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_warf_from_ratings(
            ratings=pd.Series(data=["AAA", "AA", "D"], name="foo")
        )

    assert str(err.value) == conftest.ERR_MSG


def test_get_warf_from_invalid_ratings_series():
    """Tests if function can correctly handle pd.Series objects."""
    ratings_series = pd.Series(data=[np.nan, "foo", 10], name="Fitch Ratings")
    warf_series = pd.Series(data=[np.nan, np.nan, np.nan], name="warf")

    act = rtg.get_warf_from_ratings(ratings=ratings_series)
    assert_series_equal(act, warf_series)


# --- input: ratings dataframe
exp = conftest.warf_df_wide
exp = pd.concat(
    [
        exp,
        pd.DataFrame(
            data=[[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]],
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
    "warf_ICE",
]


def test_get_warf_from_rating_scores_dataframe():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_warf_from_scores(rating_scores=conftest.scores_df_wide_with_err_row)
    assert_frame_equal(act, exp)


def test_get_warf_from_invalid_rating_scores_dataframe():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_warf_from_scores(rating_scores=conftest.input_invalid_df)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["warf_Fitch", "warf_DBRS"]
    assert_frame_equal(act, expectations)


def test_get_warf_from_ratings_dataframe_with_explicit_rating_provider():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_warf_from_ratings(
        ratings=conftest.rtg_df_wide_with_err_row,
        rating_provider=["Fitch", "Moody's", "S&P", "Bloomberg", "DBRS", "ICE"],
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


def test_get_warf_from_ratings_dataframe_by_inferring_rating_provider():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_warf_from_ratings(ratings=conftest.rtg_df_wide_with_err_row)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp)


def test_get_warf_from_ratings_dataframe_invalid_rating_provider():
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_warf_from_ratings(ratings=conftest.rtg_df_wide, rating_provider="foo")

    assert str(err.value) == conftest.ERR_MSG


def test_get_warf_from_invalid_ratings_dataframe():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_warf_from_ratings(ratings=conftest.input_invalid_df)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["warf_Fitch", "warf_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations)
