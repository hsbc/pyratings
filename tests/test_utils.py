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

"""Module contains unit tests for utils._extract_rating_provider function."""

import pytest

import pyratings as rtg
from pyratings.utils import valid_rtg_agncy
from tests import conftest

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
    ["inputs", "exp", "valid_rtg_provider"],
    [(entry1 + (entry2,)) for entry1 in ratings for entry2 in tenors],
)
def test_extract_single_rating_provider(
    inputs: str, exp: str, valid_rtg_provider: str
) -> None:
    """It returns a valid rating provider."""
    assert (
        rtg._extract_rating_provider(
            rating_provider=inputs,
            valid_rtg_provider=valid_rtg_agncy[valid_rtg_provider],
        )
        == exp
    )


def test_extract_rating_provider_shortterm_invalid_rating_provider() -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg._extract_rating_provider(
            rating_provider="Bloomberg",
            valid_rtg_provider=valid_rtg_agncy["short-term"],
        )

    assert (
        str(err.value) == "'Bloomberg' is not a valid rating provider. "
        f"'rating_provider' must be in {valid_rtg_agncy['short-term']}."
    )


@pytest.mark.parametrize("valid_rtg_provider", ["long-term", "short-term"])
def test_extract_rating_provider_invalid_str(valid_rtg_provider: str) -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg._extract_rating_provider(
            rating_provider="foo",
            valid_rtg_provider=valid_rtg_agncy[valid_rtg_provider],
        )

    if valid_rtg_provider == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG


@pytest.mark.parametrize("valid_rtg_provider", ["long-term", "short-term"])
def test_extract_rating_provider_invalid_list(valid_rtg_provider: str) -> None:
    """It raises an error message."""
    with pytest.raises(AssertionError) as err:
        rtg._extract_rating_provider(
            rating_provider=["Fitch", "foo", "Moody's"],
            valid_rtg_provider=valid_rtg_agncy[valid_rtg_provider],
        )

    if valid_rtg_provider == "long-term":
        assert str(err.value) == conftest.LT_ERR_MSG
    else:
        assert str(err.value) == conftest.ST_ERR_MSG
