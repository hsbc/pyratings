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

"""Module contains various unit tests."""
from typing import Union

import numpy as np
import pytest

import pyratings as rtg


@pytest.mark.parametrize(
    "warf, expectations",
    [
        (480, 5),
        (1, 4),
        (4000, 130),
        (54.9999, 0.0001),
        (55, 40),
        (55.0001, 39.9999),
        (9999, 0.5),
    ],
)
def test_get_warf_buffer(
    warf: Union[int, float], expectations: Union[int, float]
) -> None:
    """It returns a WARF buffer."""
    actual = rtg.get_warf_buffer(warf=warf)

    np.testing.assert_almost_equal(actual, expectations)
