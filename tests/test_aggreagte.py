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

"""Module contains unit tests for aggregation functions."""

import numpy as np
import pandas as pd

import pyratings as rtg


def test_get_weighted_average() -> None:
    """It returns a weighted avaergae."""
    rating_scores = pd.Series(
        data=[1, 5, 7, 9, np.nan, 12, 15, np.nan, 22], name="rating_scores"
    )
    weights = pd.Series(
        data=[0.1, 0.2, 0.15, 0.05, 0.1, 0.25, 0.05, 0.05, 0.05], name="weights"
    )
    actual = rtg.get_weighted_average(data=rating_scores, weights=weights)
    expectations = (
        1 * 0.1 + 5 * 0.2 + 7 * 0.15 + 9 * 0.05 + 12 * 0.25 + 15 * 0.05 + 22 * 0.05
    ) / 0.85

    np.testing.assert_almost_equal(actual, expectations)
