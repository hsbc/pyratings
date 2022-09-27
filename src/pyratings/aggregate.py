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

"""Module contains aggregation functions."""

import pandas as pd


def get_weighted_average(data: pd.Series, weights: pd.Series) -> float:
    """Compute weighted average.

    Parameters
    ----------
    data
        Contains numerical values.
    weights
        Contains weights (between 0 and 1) with respect to data.

    Returns
    -------
    float
        Weighted average data.

    Notes
    -----
    Computing the weighted average is simply the sumproduct of `data` and `weights`.
    ``nan`` in `data` will be excluded from calculating the weighted average. All
    corresponding weights will be ignored. As a matter of fact, the remaining
    weights will be upscaled so that the weights of all ``non-nan`` rows in `data` will
    sum up to 1 (100%).

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd

    >>> rtg_scores = pd.Series(data=[5, 7, 9])
    >>> wgt = pd.Series(data=[0.5, 0.3, 0.2])
    >>> get_weighted_average(data=rtg_scores, weights=wgt)
    6.4

    >>> warf = pd.Series(data=[500, 735, np.nan, 93, np.nan])
    >>> wgt = pd.Series(data=[0.4, 0.1, 0.1, 0.2, 0.2])
    >>> get_weighted_average(data=warf, weights=wgt)
    417.29
    """
    # find indices in warf that correspond to np.nan
    idx_nan = data[pd.isna(data)].index

    # sum weights of securities with an actual rating, i.e. rating is not NaN
    weights_non_nan = 1 - sum(weights.loc[idx_nan])

    # upscale to 100%
    weights_upscaled = weights / weights_non_nan

    return data.fillna(0).dot(weights_upscaled)
