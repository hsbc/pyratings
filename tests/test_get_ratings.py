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


# --- input: single score/warf
@pytest.mark.parametrize(
    ["rating_provider", "score", "rating"],
    list(
        pd.concat(
            [
                conftest.scores_df_long,
                conftest.rtg_df_long["rating"],
            ],
            axis=1,
        ).to_records(index=False)
    ),
)
def test_get_rating_from_single_score_longterm(rating_provider, score, rating):
    """Tests if function can handle single string objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=score, rating_provider=rating_provider, tenor="long-term"
    )

    assert act == rating


def test_get_rating_from_single_score_float_longterm():
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
    ["rating_provider", "score", "rating"],
    list(
        pd.concat(
            [
                conftest.scores_df_long_st,
                conftest.rtg_df_long_st["rating"],
            ],
            axis=1,
        ).to_records(index=False)
    ),
)
def test_get_rating_from_single_score_shortterm(rating_provider, score, rating):
    """Tests if function can handle single string objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=score, rating_provider=rating_provider, tenor="short-term"
    )

    assert act == rating


def test_get_rating_from_single_score_float_shortterm():
    assert (
        rtg.get_ratings_from_scores(
            rating_scores=5.499, rating_provider="DBRS", tenor="short-term"
        )
        == "R-2 (high)"
    )
    assert (
        rtg.get_ratings_from_scores(
            rating_scores=5.501, rating_provider="DBRS", tenor="short-term"
        )
        == "R-2 (mid)"
    )


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_single_score_invalid_rating_provider(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=10, rating_provider="foo", tenor=tenor
        )
    assert str(err.value) == conftest.ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_with_invalid_single_score(tenor):
    """Tests if function returns NaN for invalid inputs."""
    act = rtg.get_ratings_from_scores(
        rating_scores=-5, rating_provider="Fitch", tenor=tenor
    )
    assert pd.isna(act)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_with_single_score_and_no_rating_provider(tenor):
    """Tests if correct error message will be raised."""
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
def test_get_ratings_from_single_warf(warf, rating_provider, rating):
    """Tests if function can correctly handle individual warf (float)."""
    act = rtg.get_ratings_from_warf(warf=warf, rating_provider=rating_provider)
    assert act == rating


def test_get_ratings_from_single_warf_with_no_rating_provider():
    """Tests if correct error message will be raised."""
    with pytest.raises(ValueError) as err:
        rtg.get_ratings_from_warf(warf=100, rating_provider=None)

    assert str(err.value) == "'rating_provider' must not be None."


@pytest.mark.parametrize("warf", [np.nan, -5, 20000])
def test_get_ratings_from_invalid_single_warf(warf):
    """Tests if function returns NaN for invalid inputs."""
    assert pd.isna(rtg.get_ratings_from_warf(warf=warf, rating_provider="DBRS"))


# --- input: ratings score series
@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.params_provider_scores_ratings_lt,
)
def test_get_ratings_from_scores_series_longterm(
    rating_provider, scores_series, ratings_series
):
    """Tests if function can correctly handle pd.Series objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=scores_series, rating_provider=rating_provider
    )
    ratings_series.name = f"rtg_{rating_provider}"
    assert_series_equal(act, ratings_series)


@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.params_provider_scores_ratings_lt,
)
def test_get_ratings_from_scores_series_longterm_float(
    rating_provider, scores_series, ratings_series
):
    """Tests if function can correctly handle pd.Series objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=scores_series.add(0.23), rating_provider=rating_provider
    )
    ratings_series.name = f"rtg_{rating_provider}"
    assert_series_equal(act, ratings_series)


@pytest.mark.parametrize(
    ["rating_provider", "scores_series", "ratings_series"],
    conftest.params_provider_scores_ratings_st,
)
def test_get_ratings_from_scores_series_shortterm(
    rating_provider, scores_series, ratings_series
):
    """Tests if function can correctly handle pd.Series objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=scores_series, rating_provider=rating_provider, tenor="short-term"
    )
    ratings_series.name = f"rtg_{rating_provider}"
    assert_series_equal(act, ratings_series)


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_scores_series_invalid_rating_provider(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=pd.Series(data=[1, 3, 22], name="rtg_score"),
            rating_provider="foo",
            tenor=tenor,
        )

    assert str(err.value) == conftest.ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_scores_series_with_no_rating_provider(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=pd.Series(data=[1, 3, 22], name="foo"),
            tenor=tenor,
        )

    assert str(err.value) == conftest.ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_invalid_scores_series(tenor):
    """Tests if function can correctly handle pd.Series objects."""
    scores_series = pd.Series(data=[np.nan, "foo", -10], name="rtg_score")
    ratings_series = pd.Series(data=[np.nan, np.nan, np.nan], name="rating")

    act = rtg.get_ratings_from_scores(
        rating_scores=scores_series, rating_provider="Fitch", tenor=tenor
    )
    ratings_series.name = "rtg_Fitch"
    assert_series_equal(act, ratings_series, check_dtype=False)


@pytest.mark.parametrize(
    ["rating_provider", "warf_series", "ratings_series"],
    conftest.params_provider_warf_ratings,
)
def test_get_ratings_from_warf_series(rating_provider, warf_series, ratings_series):
    """Tests if function can correctly handle pd.Series objects."""
    act = rtg.get_ratings_from_warf(warf=warf_series, rating_provider=rating_provider)
    ratings_series.name = f"rtg_{rating_provider}"
    assert_series_equal(act, ratings_series)


def test_get_ratings_from_invalid_warf_series():
    """Tests if function can correctly handle pd.Series objects."""
    warf_series = pd.Series(data=[np.nan, "foo", -10], name="rtg_score")
    ratings_series = pd.Series(data=[np.nan, np.nan, np.nan], name="rating")

    act = rtg.get_ratings_from_warf(warf=warf_series, rating_provider="Fitch")
    ratings_series.name = "rtg_Fitch"
    assert_series_equal(act, ratings_series, check_dtype=False)


# --- input: rating score dataframe
exp_lt = conftest.rtg_df_wide
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

exp_st = conftest.rtg_df_wide_st
exp_st = pd.concat(
    [
        exp_st,
        pd.DataFrame(
            data=[[np.nan, np.nan, np.nan, np.nan]],
            columns=exp_st.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)
exp_st.columns = [
    "rtg_Fitch",
    "rtg_Moody",
    "rtg_SP",
    "rtg_DBRS",
]


def test_get_ratings_from_scores_dataframe_with_explicit_rating_provider_longterm():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=conftest.scores_df_wide_with_err_row,
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


def test_get_ratings_from_scores_dataframe_with_explicit_rating_provider_shortterm():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=conftest.scores_df_wide_st_with_err_row,
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


def test_get_ratings_from_scores_dataframe_by_inferring_rating_provider_longterm():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=conftest.scores_df_wide_with_err_row
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


def test_get_ratings_from_scores_dataframe_by_inferring_rating_provider_shortterm():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=conftest.scores_df_wide_st_with_err_row, tenor="short-term"
    )
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_st)


def test_get_ratings_from_scores_dataframe_by_inferring_rating_provider_lt_float():
    """Tests if function can correctly handle pd.DataFrame objects."""
    scores_df_wide_float = conftest.scores_df_wide + 0.23
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
def test_get_ratings_from_scores_dataframe_invalid_rating_provider(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_ratings_from_scores(
            rating_scores=conftest.scores_df_wide, rating_provider="foo", tenor=tenor
        )
    assert str(err.value) == conftest.ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_get_ratings_from_invalid_rating_scores_dataframe(tenor):
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_ratings_from_scores(
        rating_scores=conftest.input_invalid_df, tenor=tenor
    )
    expectations = conftest.exp_invalid_df
    expectations.columns = ["rtg_Fitch", "rtg_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations, check_dtype=False)


def test_get_ratings_from_warf_dataframe():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_ratings_from_warf(warf=conftest.warf_df_wide_with_err_row)
    # noinspection PyTypeChecker
    assert_frame_equal(act, exp_lt)


def test_get_ratings_from_invalid_warf_dataframe():
    """Tests if function can correctly handle pd.DataFrame objects."""
    act = rtg.get_ratings_from_warf(warf=conftest.input_invalid_df)
    expectations = conftest.exp_invalid_df
    expectations.columns = ["rtg_Fitch", "rtg_DBRS"]
    # noinspection PyTypeChecker
    assert_frame_equal(act, expectations, check_dtype=False)
