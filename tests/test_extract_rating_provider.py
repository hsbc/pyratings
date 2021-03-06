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
import pytest

import pyratings as rtg
from tests import conftest


@pytest.mark.parametrize("rating_agency", conftest.rating_provider_lt_list)
def test_extract_rating_provider_single_rating_provider_longterm(rating_agency):
    """Tests input parsing for single rating provider with long-term tenor."""
    rtg._assert_rating_provider(rating_provider=rating_agency, tenor="long-term")


@pytest.mark.parametrize("rating_agency", conftest.rating_provider_st_list)
def test_extract_rating_provider_single_rating_provider_shortterm(rating_agency):
    """Tests input parsing for single rating provider with short-term tenor."""
    rtg._assert_rating_provider(rating_provider=rating_agency, tenor="short-term")


def test_extract_rating_provider_multiple_rating_provider_longterm():
    """Tests input parsing for multiple rating provider with long-term tenor."""
    rtg._assert_rating_provider(
        rating_provider=conftest.rating_provider_lt_list, tenor="long-term"
    )


def test_extract_rating_provider_multiple_rating_provider_shortterm():
    """Tests input parsing for multiple rating provider with short-term tenor."""
    rtg._assert_rating_provider(
        rating_provider=conftest.rating_provider_st_list, tenor="short-term"
    )


ratings = [
    ("Fitch", "Fitch"),
    ("fitch", "Fitch"),
    ("rtg_Fitch", "Fitch"),
    ("rtg_fitch", "Fitch"),
    ("rtg_Fitch2", "Fitch"),
    ("rtg_fitch2", "Fitch"),
    ("Moody's", "Moody"),
    ("MOODY'S", "Moody"),
    ("S&P", "SP"),
    ("&S&P&", "SP"),
    (["S&P", "rtg_mooDY'S23", "123DBRSDBRS"], ["SP", "Moody", "DBRS"]),
]

tenors = ("long-term", "short-term")


@pytest.mark.parametrize(
    ["inputs", "exp", "tenor"],
    [(entry1 + (entry2,)) for entry1 in ratings for entry2 in tenors],
)
def test_extract_single_rating_provider(inputs, exp, tenor):
    """Tests if rating agencies will get extracted correctly."""
    assert rtg._extract_rating_provider(rating_provider=inputs, tenor=tenor) == exp


def test_extract_rating_provider_shortterm_invalid_rating_provider():
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg._extract_rating_provider(rating_provider="Bloomberg", tenor="short-term")

    assert (
        str(err.value) == "rating_provider must be in ['Moody', 'SP', 'Fitch', 'DBRS']."
    )


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_extract_rating_provider_invalid_str(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg._extract_rating_provider(rating_provider="foo", tenor=tenor)

    assert str(err.value) == conftest.ERR_MSG


@pytest.mark.parametrize("tenor", ["long-term", "short-term"])
def test_extract_rating_provider_invalid_list(tenor):
    """Tests if correct error message will be raised."""
    with pytest.raises(AssertionError) as err:
        rtg._extract_rating_provider(
            rating_provider=["Fitch", "foo", "Moody's"], tenor=tenor
        )

    assert str(err.value) == conftest.ERR_MSG
