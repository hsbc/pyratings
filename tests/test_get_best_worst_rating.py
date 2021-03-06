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

import pyratings as rtg
from tests import conftest


@pytest.fixture(scope="session")
def rtg_inputs_longterm():
    return pd.DataFrame(
        data={
            "rtg_sp": ["AAA", "AA-", "AA+", "BB-", "C", np.nan, "BBB+", "AA"],
            "rtg_moody": ["Aa1", "Aa3", "Aa2", "Ba3", "Ca", np.nan, np.nan, "Aa2"],
            "rtg_fitch": ["AA-", np.nan, "AA-", "B+", "C", np.nan, np.nan, "AA"],
        }
    )


@pytest.fixture(scope="session")
def rtg_inputs_shortterm():
    return pd.DataFrame(
        data={
            "rtg_sp": ["A-1", "A-3", "A-1+", "D", "B", np.nan, "A-2", "A-3"],
            "rtg_moody": ["P-2", "NP", "P-1", "NP", "P-3", np.nan, np.nan, "P-3"],
            "rtg_fitch": ["F1", np.nan, "F1", "F3", "F3", np.nan, np.nan, "F3"],
        }
    )


def test_get_best_rating_longterm_with_explicit_rating_provider(rtg_inputs_longterm):
    """Test computation of best ratings on a security (line-by-line) basis."""
    actual = rtg.get_best_ratings(
        rtg_inputs_longterm,
        rating_provider_input=["SP", "Moody", "Fitch"],
        tenor="long-term",
    )

    expectations = pd.Series(
        data=["AAA", "AA-", "AA+", "BB-", "CC", np.nan, "BBB+", "AA"], name="best_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_best_rating_longterm_with_inferring_rating_provider(rtg_inputs_longterm):
    """Test computation of best ratings on a security (line-by-line) basis."""
    actual = rtg.get_best_ratings(rtg_inputs_longterm, tenor="long-term")

    expectations = pd.Series(
        data=["AAA", "AA-", "AA+", "BB-", "CC", np.nan, "BBB+", "AA"], name="best_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_best_rating_shortterm_with_explicit_rating_provider(rtg_inputs_shortterm):
    """Test computation of best ratings on a security (line-by-line) basis."""
    actual = rtg.get_best_ratings(
        rtg_inputs_shortterm,
        rating_provider_input=["SP", "Moody", "Fitch"],
        tenor="short-term",
    )

    expectations = pd.Series(
        data=["A-1", "A-3", "A-1+", "A-3", "A-3", np.nan, "A-2", "A-3"], name="best_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_best_rating_shortterm_with_inferring_rating_provider(rtg_inputs_shortterm):
    """Test computation of best ratings on a security (line-by-line) basis."""
    actual = rtg.get_best_ratings(rtg_inputs_shortterm, tenor="short-term")

    expectations = pd.Series(
        data=["A-1", "A-3", "A-1+", "A-3", "A-3", np.nan, "A-2", "A-3"], name="best_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_second_best_rating_longterm_with_explicit_rating_provider(
    rtg_inputs_longterm,
):
    """Test computation of second-best ratings on a security (line-by-line) basis."""
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
    rtg_inputs_longterm,
):
    """Test computation of best ratings on a security (line-by-line) basis."""
    actual = rtg.get_second_best_ratings(rtg_inputs_longterm, tenor="long-term")

    expectations = pd.Series(
        data=["AA+", "AA-", "AA", "BB-", "C", np.nan, "BBB+", "AA"],
        name="second_best_rtg",
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_second_best_rating_shortterm_with_explicit_rating_provider(
    rtg_inputs_shortterm,
):
    """Test computation of best ratings on a security (line-by-line) basis."""
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
    rtg_inputs_shortterm,
):
    """Test computation of best ratings on a security (line-by-line) basis."""
    actual = rtg.get_second_best_ratings(rtg_inputs_shortterm, tenor="short-term")

    expectations = pd.Series(
        data=["A-1", "B", "A-1+", "B", "A-3", np.nan, "A-2", "A-3"],
        name="second_best_rtg",
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_worst_rating_longterm_with_explicit_rating_provider(
    rtg_inputs_longterm,
):
    """Test computation of second-best ratings on a security (line-by-line) basis."""
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
    rtg_inputs_longterm,
):
    """Test computation of best ratings on a security (line-by-line) basis."""
    actual = rtg.get_worst_ratings(rtg_inputs_longterm, tenor="long-term")

    expectations = pd.Series(
        data=["AA-", "AA-", "AA-", "B+", "C", np.nan, "BBB+", "AA"], name="worst_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_worst_rating_shortterm_with_explicit_rating_provider(
    rtg_inputs_shortterm,
):
    """Test computation of best ratings on a security (line-by-line) basis."""
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
    rtg_inputs_shortterm,
):
    """Test computation of best ratings on a security (line-by-line) basis."""
    actual = rtg.get_worst_ratings(rtg_inputs_shortterm, tenor="short-term")

    expectations = pd.Series(
        data=["A-2", "B", "A-1", "D", "B", np.nan, "A-2", "A-3"], name="worst_rtg"
    )

    pd.testing.assert_series_equal(actual, expectations)


def test_get_worst_rating_longterm_invalid_provider():
    """Test if the correct error message will be raised."""
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

    assert str(err.value) == conftest.ERR_MSG


def test_get_worst_rating_shortterm_invalid_provider():
    """Test if the correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg.get_worst_ratings(
            pd.DataFrame(
                data={
                    "ICE": ["AAA", "BBB"],
                    "DBRS": ["B+", "CCC"],
                }
            ),
            rating_provider_input=["ICE", "DBRS"],
            tenor="short-term",
        )

    assert str(err.value) == (
        "rating_provider must be in ['Moody', 'SP', 'Fitch', 'DBRS']."
    )
