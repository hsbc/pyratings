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

"""Module contains unit tests for consolidation of ratings."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import pyratings as rtg
from tests import conftest


@pytest.fixture(scope="session")
def rtg_inputs_longterm() -> pd.DataFrame:
    """Return a dataframe with long-term ratings from the main rating agencies."""
    return pd.DataFrame(
        data={
            "rtg_sp": ["AAA", "AA-", "AA+", "BB-", "C", np.nan, "BBB+", "AA"],
            "rtg_moody": ["Aa1", "Aa3", "Aa2", "Ba3", "Ca", np.nan, np.nan, "Aa2"],
            "rtg_fitch": ["AA-", np.nan, "AA-", "B+", "C", np.nan, np.nan, "AA"],
        }
    )


@pytest.fixture(scope="session")
def rtg_inputs_shortterm() -> pd.DataFrame:
    """Return a dataframe with short-term ratings from the main rating agencies."""
    return pd.DataFrame(
        data={
            "rtg_sp": ["A-1", "A-3", "A-1+", "D", "B", np.nan, "A-2", "A-3"],
            "rtg_moody": ["P-2", "NP", "P-1", "NP", "P-3", np.nan, np.nan, "P-3"],
            "rtg_fitch": ["F1", np.nan, "F1", "F3", "F3", np.nan, np.nan, "F3"],
        }
    )


@pytest.mark.parametrize("rating_provider_input", (["SP", "Moody", "Fitch"], None))
def test_get_best_rating_scores_long_term(
    rtg_inputs_longterm: pd.DataFrame, rating_provider_input: list[str] | None
) -> None:
    """It returns the best long-term scores on a security (line-by-line) basis."""
    actual = rtg.get_best_scores(
        ratings=rtg_inputs_longterm,
        rating_provider_input=rating_provider_input,
        tenor="long-term",
    )

    expectations = pd.Series(
        data=[1.0, 4.0, 2.0, 13.0, 20, np.nan, 8, 3], name="best_scores"
    )

    pd.testing.assert_series_equal(actual, expectations)


@pytest.mark.parametrize("rating_provider_input", (["SP", "Moody", "Fitch"], None))
def test_get_best_rating_scores_shortterm(
    rtg_inputs_shortterm: pd.DataFrame,
    rating_provider_input: list[str] | None,
) -> None:
    """It returns the best short-term scores on a security (line-by-line) basis."""
    actual = rtg.get_best_scores(
        rtg_inputs_shortterm,
        rating_provider_input=rating_provider_input,
        tenor="short-term",
    )

    expectations = pd.Series(
        data=[5.5, 10.0, 2.5, 9.5, 9.5, np.nan, 8.0, 9.5], name="best_scores"
    )

    pd.testing.assert_series_equal(actual, expectations)


@pytest.mark.parametrize("rating_provider_input", (["SP", "Moody", "Fitch"], None))
def test_get_second_best_rating_scores_long_term(
    rtg_inputs_longterm: pd.DataFrame, rating_provider_input: list[str] | None
) -> None:
    """It returns the second-best lt scores on a security (line-by-line) basis."""
    actual = rtg.get_second_best_scores(
        ratings=rtg_inputs_longterm,
        rating_provider_input=rating_provider_input,
        tenor="long-term",
    )

    expectations = pd.Series(
        data=[2.0, 4.0, 3.0, 13.0, 21, np.nan, 8, 3], name="second_best_scores"
    )

    pd.testing.assert_series_equal(actual, expectations)


@pytest.mark.parametrize("rating_provider_input", (["SP", "Moody", "Fitch"], None))
def test_get_second_best_rating_scores_shortterm(
    rtg_inputs_shortterm: pd.DataFrame,
    rating_provider_input: list[str] | None,
) -> None:
    """It returns the best short-term scores on a security (line-by-line) basis."""
    actual = rtg.get_second_best_scores(
        rtg_inputs_shortterm,
        rating_provider_input=rating_provider_input,
        tenor="short-term",
    )

    expectations = pd.Series(
        data=[6.5, 16.5, 3.5, 16.5, 9.5, np.nan, 8.0, 9.5], name="second_best_scores"
    )

    pd.testing.assert_series_equal(actual, expectations)


@pytest.mark.parametrize("rating_provider_input", (["SP", "Moody", "Fitch"], None))
def test_get_worst_rating_scores_long_term(
    rtg_inputs_longterm: pd.DataFrame, rating_provider_input: list[str] | None
) -> None:
    """It returns the worst long-term scores on a security (line-by-line) basis."""
    actual = rtg.get_worst_scores(
        ratings=rtg_inputs_longterm,
        rating_provider_input=rating_provider_input,
        tenor="long-term",
    )

    expectations = pd.Series(
        data=[4.0, 4.0, 4.0, 14.0, 21, np.nan, 8, 3], name="worst_scores"
    )

    pd.testing.assert_series_equal(actual, expectations)


@pytest.mark.parametrize("rating_provider_input", (["SP", "Moody", "Fitch"], None))
def test_get_worst_rating_scores_shortterm(
    rtg_inputs_shortterm: pd.DataFrame,
    rating_provider_input: list[str] | None,
) -> None:
    """It returns the worst short-term scores on a security (line-by-line) basis."""
    actual = rtg.get_worst_scores(
        rtg_inputs_shortterm,
        rating_provider_input=rating_provider_input,
        tenor="short-term",
    )

    expectations = pd.Series(
        data=[7.5, 16.5, 6.5, 22.0, 13.5, np.nan, 8.0, 10.0], name="worst_scores"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_best_rating_longterm_with_explicit_rating_provider(
    rtg_inputs_longterm: pd.DataFrame,
) -> None:
    """It returns the best long-term ratings on a security (line-by-line) basis."""
    actual = rtg.get_best_ratings(
        rtg_inputs_longterm,
        rating_provider_input=["SP", "Moody", "Fitch"],
        tenor="long-term",
    )

    expectations = pd.Series(
        data=["AAA", "AA-", "AA+", "BB-", "CC", np.nan, "BBB+", "AA"], name="best_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_best_rating_longterm_with_inferring_rating_provider(
    rtg_inputs_longterm: pd.DataFrame,
) -> None:
    """It returns the best long-term ratings on a security (line-by-line) basis."""
    actual = rtg.get_best_ratings(rtg_inputs_longterm, tenor="long-term")

    expectations = pd.Series(
        data=["AAA", "AA-", "AA+", "BB-", "CC", np.nan, "BBB+", "AA"], name="best_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_best_rating_shortterm_with_explicit_rating_provider(
    rtg_inputs_shortterm: pd.DataFrame,
) -> None:
    """It returns the best short-term ratings on a security (line-by-line) basis."""
    actual = rtg.get_best_ratings(
        rtg_inputs_shortterm,
        rating_provider_input=["SP", "Moody", "Fitch"],
        tenor="short-term",
    )

    expectations = pd.Series(
        data=["A-1", "A-3", "A-1+", "A-3", "A-3", np.nan, "A-2", "A-3"], name="best_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_best_rating_shortterm_with_inferring_rating_provider(
    rtg_inputs_shortterm: pd.DataFrame,
) -> None:
    """It returns the best short-term ratings on a security (line-by-line) basis."""
    actual = rtg.get_best_ratings(rtg_inputs_shortterm, tenor="short-term")

    expectations = pd.Series(
        data=["A-1", "A-3", "A-1+", "A-3", "A-3", np.nan, "A-2", "A-3"], name="best_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_second_best_rating_longterm_with_explicit_rating_provider(
    rtg_inputs_longterm: pd.DataFrame,
) -> None:
    """It returns the second-best lt ratings on a security (line-by-line) basis."""
    actual = rtg.get_second_best_ratings(
        rtg_inputs_longterm,
        rating_provider_input=["SP", "Moody", "Fitch"],
        tenor="long-term",
    )

    expectations = pd.Series(
        data=["AA+", "AA-", "AA", "BB-", "C", np.nan, "BBB+", "AA"],
        name="second_best_rtg",
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_second_best_rating_longterm_with_inferring_rating_provider(
    rtg_inputs_longterm: pd.DataFrame,
) -> None:
    """It returns the second-best lt ratings on a security (line-by-line) basis."""
    actual = rtg.get_second_best_ratings(rtg_inputs_longterm, tenor="long-term")

    expectations = pd.Series(
        data=["AA+", "AA-", "AA", "BB-", "C", np.nan, "BBB+", "AA"],
        name="second_best_rtg",
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_second_best_rating_shortterm_with_explicit_rating_provider(
    rtg_inputs_shortterm: pd.DataFrame,
) -> None:
    """It returns the second-best st ratings on a security (line-by-line) basis."""
    actual = rtg.get_second_best_ratings(
        rtg_inputs_shortterm,
        rating_provider_input=["SP", "Moody", "Fitch"],
        tenor="short-term",
    )

    expectations = pd.Series(
        data=["A-1", "B", "A-1+", "B", "A-3", np.nan, "A-2", "A-3"],
        name="second_best_rtg",
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_second_best_rating_shortterm_with_inferring_rating_provider(
    rtg_inputs_shortterm: pd.DataFrame,
) -> None:
    """It returns the second-best st ratings on a security (line-by-line) basis."""
    actual = rtg.get_second_best_ratings(rtg_inputs_shortterm, tenor="short-term")

    expectations = pd.Series(
        data=["A-1", "B", "A-1+", "B", "A-3", np.nan, "A-2", "A-3"],
        name="second_best_rtg",
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_worst_rating_longterm_with_explicit_rating_provider(
    rtg_inputs_longterm: pd.DataFrame,
) -> None:
    """It returns the worst long-term ratings on a security (line-by-line) basis."""
    actual = rtg.get_worst_ratings(
        rtg_inputs_longterm,
        rating_provider_input=["SP", "Moody", "Fitch"],
        tenor="long-term",
    )

    expectations = pd.Series(
        data=["AA-", "AA-", "AA-", "B+", "C", np.nan, "BBB+", "AA"], name="worst_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_worst_rating_longterm_with_inferring_rating_provider(
    rtg_inputs_longterm: pd.DataFrame,
) -> None:
    """It returns the worst long-term ratings on a security (line-by-line) basis."""
    actual = rtg.get_worst_ratings(rtg_inputs_longterm, tenor="long-term")

    expectations = pd.Series(
        data=["AA-", "AA-", "AA-", "B+", "C", np.nan, "BBB+", "AA"], name="worst_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_worst_rating_shortterm_with_explicit_rating_provider(
    rtg_inputs_shortterm: pd.DataFrame,
) -> None:
    """It returns the worst short-term ratings on a security (line-by-line) basis."""
    actual = rtg.get_worst_ratings(
        rtg_inputs_shortterm,
        rating_provider_input=["SP", "Moody", "Fitch"],
        tenor="short-term",
    )

    expectations = pd.Series(
        data=["A-2", "B", "A-1", "D", "B", np.nan, "A-2", "A-3"], name="worst_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_worst_rating_shortterm_with_inferring_rating_provider(
    rtg_inputs_shortterm: pd.DataFrame,
) -> None:
    """It returns the worst short-term ratings on a security (line-by-line) basis."""
    actual = rtg.get_worst_ratings(rtg_inputs_shortterm, tenor="short-term")

    expectations = pd.Series(
        data=["A-2", "B", "A-1", "D", "B", np.nan, "A-2", "A-3"], name="worst_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_worst_rating_longterm_invalid_provider() -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_worst_ratings(
            pd.DataFrame(
                data={
                    "foo": ["AAA", "BBB"],
                    "Bloomberg": ["B+", "CCC"],
                }
            ),
            rating_provider_input=["foo", "Bloomberg"],
            tenor="long-term",
        )

    assert str(err.value) == conftest.LT_ERR_MSG


def test_get_worst_rating_shortterm_invalid_provider() -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg.get_worst_ratings(
            pd.DataFrame(
                data={
                    "foo": ["AAA", "BBB"],
                    "DBRS": ["B+", "CCC"],
                }
            ),
            rating_provider_input=["foo", "DBRS"],
            tenor="short-term",
        )

    assert str(err.value) == (
        "'foo' is not a valid rating provider. 'rating_provider' must be in "
        "['fitch', 'moody', 'sp', 's&p', 'dbrs']."
    )
