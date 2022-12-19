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

"""Module holds various variables and fixtures used in different unit tests."""

import numpy as np
import pandas as pd

# --- ratings --------------------------------------------------------------------------
# --- long-term
lt_rtg_prov_list = ["Fitch", "Moody", "SP", "Bloomberg", "DBRS"]

lt_rtg_df_wide = pd.DataFrame(
    data=[
        ["AAA", "Aaa", "AAA", "AAA", "AAA"],
        ["AA+", "Aa1", "AA+", "AA+", "AAH"],
        ["AA", "Aa2", "AA", "AA", "AA"],
        ["AA-", "Aa3", "AA-", "AA-", "AAL"],
        ["A+", "A1", "A+", "A+", "AH"],
        ["A", "A2", "A", "A", "A"],
        ["A-", "A3", "A-", "A-", "AL"],
        ["BBB+", "Baa1", "BBB+", "BBB+", "BBBH"],
        ["BBB", "Baa2", "BBB", "BBB", "BBB"],
        ["BBB-", "Baa3", "BBB-", "BBB-", "BBBL"],
        ["BB+", "Ba1", "BB+", "BB+", "BBH"],
        ["BB", "Ba2", "BB", "BB", "BB"],
        ["BB-", "Ba3", "BB-", "BB-", "BBL"],
        ["B+", "B1", "B+", "B+", "BH"],
        ["B", "B2", "B", "B", "B"],
        ["B-", "B3", "B-", "B-", "BL"],
        ["CCC+", "Caa1", "CCC+", "CCC+", "CCCH"],
        ["CCC", "Caa2", "CCC", "CCC", "CCC"],
        ["CCC-", "Caa3", "CCC-", "CCC-", "CCCL"],
        ["CC", "Ca", "CC", "CC", "CC"],
        ["C", "C", "C", "C", "C"],
        ["D", "D", "D", "DDD", "D"],
    ],
    columns=lt_rtg_prov_list,
)

lt_rtg_df_wide_with_err_row = pd.concat(
    [
        lt_rtg_df_wide,
        pd.DataFrame(
            data=[["foo", "foo", "foo", "foo", "foo"]],
            columns=lt_rtg_df_wide.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)

lt_rtg_df_wide_with_watch_unsolicited = pd.DataFrame(
    data=[
        ["AAA (Developing)", "Aaa", "AAA", "AAA", "AAA"],
        ["AA+", "(P)Aa1", "AA+", "AA+", "AAH"],
        ["AA", "(p)Aa2", "AA", "AA", "AA *-"],
        ["AA-", "Aa3", "AA-", "AA-", "AAL"],
        ["A+", "A1", "A+", "A+", "AH"],
        ["A", "A2", "A", "A", "A"],
        ["A-", "A3", "A-", "A-", "AL"],
        ["BBB+", "Baa1", "BBB+", "BBB+ (CwPositive)", "BBBH"],
        ["BBB", "Baa2", "BBB", "BBB", "BBB"],
        ["BBB-", "Baa3", "BBB- *-", "BBB-", "BBBL"],
        ["BB+", "Ba1", "BB+U", "BB+", "BBH"],
        ["BB", "Ba2", "BB", "BB", "BB"],
        ["BB-", "Ba3", "BB-", "BB-u", "BBL"],
        ["B+", "B1", "B+", "B+", "BH"],
        ["B", "B2", "B", "B", "B"],
        ["B-", "B3", "B-", "B-", "BL"],
        ["CCC+", "Caa1", "CCC+", "CCC+", "CCCH"],
        ["CCC", "Caa2", "CCCu", "CCC", "CCC"],
        ["CCC-", "Caa3u", "CCC-", "CCC-", "CCCL"],
        ["CCu", "Ca", "CC", "CC", "CC"],
        ["C", "C", "C", "C", "C"],
        ["D", "D", "D", "DDD", "D"],
    ],
    columns=lt_rtg_prov_list,
)
lt_rtg_df_long = pd.melt(
    lt_rtg_df_wide, var_name="rating_provider", value_name="rating"
)

lt_rtg_df_long_with_watch_unsolicited = pd.melt(
    lt_rtg_df_wide_with_watch_unsolicited,
    var_name="rating_provider",
    value_name="rating",
)

lt_scores_df_wide = pd.DataFrame(
    data=[
        [1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3],
        [4, 4, 4, 4, 4],
        [5, 5, 5, 5, 5],
        [6, 6, 6, 6, 6],
        [7, 7, 7, 7, 7],
        [8, 8, 8, 8, 8],
        [9, 9, 9, 9, 9],
        [10, 10, 10, 10, 10],
        [11, 11, 11, 11, 11],
        [12, 12, 12, 12, 12],
        [13, 13, 13, 13, 13],
        [14, 14, 14, 14, 14],
        [15, 15, 15, 15, 15],
        [16, 16, 16, 16, 16],
        [17, 17, 17, 17, 17],
        [18, 18, 18, 18, 18],
        [19, 19, 19, 19, 19],
        [20, 20, 20, 20, 20],
        [21, 21, 21, 21, 21],
        [22, 22, 22, 22, 22],
    ],
    columns=lt_rtg_prov_list,
)
lt_scores_df_long = pd.melt(
    lt_scores_df_wide, var_name="rating_provider", value_name="rtg_score"
)

lt_scores_df_wide_with_err_row = pd.concat(
    [
        lt_scores_df_wide,
        pd.DataFrame(
            data=[["foo", "foo", "foo", "foo", "foo"]],
            columns=lt_scores_df_wide.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)

lt_prov_scrs_rtg = [
    (
        rating_provider,
        lt_scores_df_long.loc[
            lt_scores_df_long["rating_provider"] == rating_provider,
            "rtg_score",
        ]
        .reset_index(drop=True)
        .squeeze(),
        lt_rtg_df_long.loc[
            lt_rtg_df_long["rating_provider"] == rating_provider,
            ["rating"],
        ]
        .reset_index(drop=True)
        .squeeze(),
    )
    for rating_provider in lt_rtg_prov_list
]

# --- short term
st_rtg_prov_list = ["Fitch", "Moody", "SP", "DBRS"]

st_strategies = ["best", "base", "worst"]
st_rtgs = {
    "Fitch": ["F1+", "F1", "F2", "F3", "B", "C", "D"],
    "Moody": ["P-1", "P-2", "P-3", "NP"],
    "SP": ["A-1+", "A-1", "A-2", "A-3", "B", "C", "D"],
}
st_rtg_dict = {
    "best": {
        "Fitch": st_rtgs["Fitch"],
        "Moody": st_rtgs["Moody"],
        "SP": st_rtgs["SP"],
        "DBRS": [
            "R-1H",
            "R-1M",
            "R-1L",
            "R-2H",
            "R-2M",
            "R-3",
            "R-4",
            "R-5",
            "D",
        ],
    },
    "base": {
        "Fitch": st_rtgs["Fitch"],
        "Moody": st_rtgs["Moody"],
        "SP": st_rtgs["SP"],
        "DBRS": [
            "R-1H",
            "R-1M",
            "R-1L",
            "R-2H",
            "R-2M",
            "R-2L / R-3",
            "R-4",
            "R-5",
            "D",
        ],
    },
    "worst": {
        "Fitch": st_rtgs["Fitch"],
        "Moody": st_rtgs["Moody"],
        "SP": st_rtgs["SP"],
        "DBRS": [
            "R-1H",
            "R-1M",
            "R-1L",
            "R-2H",
            "R-2M",
            "R-3",
            "R-4",
            "R-5",
            "D",
        ],
    },
}

st_scrs_dict = {
    "best": {
        "Fitch": [3.5, 7.5, 9.0, 10.0, 13.5, 18.5, 21.5],
        "Moody": [4.0, 8.5, 10.0, 16.5],
        "SP": [3.0, 6.5, 8.5, 10.5, 14.0, 19.0, 22.0],
        "DBRS": [2.0, 4.5, 7.0, 9.0, 10.0, 11.0, 13.5, 18.5, 22.0],
    },
    "base": {
        "Fitch": [3.0, 6.5, 8.0, 9.5, 13.5, 18.5, 21.5],
        "Moody": [3.5, 7.5, 9.5, 16.5],
        "SP": [2.5, 5.5, 8.0, 10.0, 13.5, 19.0, 22.0],
        "DBRS": [1.5, 3.5, 6.0, 8.0, 9.0, 10.0, 12.5, 18.0, 22.0],
    },
    "worst": {
        "Fitch": [2.5, 5.5, 7.5, 9.5, 13.5, 18.5, 21.5],
        "Moody": [3.0, 7.0, 9.5, 16.5],
        "SP": [2.5, 5.5, 8.0, 10.0, 13.5, 19.0, 22.0],
        "DBRS": [1.0, 2.5, 5.0, 7.5, 9.0, 10.0, 12.5, 18.0, 22.0],
    },
}

# create list of tuples for parameterization: [(Strategy, RatingProvider, Rating,
# RatingScore), ]
st_strat_prov_rtg_scrs_records = []
for strat in st_strategies:
    for (k, v_rtg, v_scores) in zip(
        st_rtg_prov_list, st_rtg_dict[strat].values(), st_scrs_dict[strat].values()
    ):
        for (x, y) in zip(v_rtg, v_scores):
            st_strat_prov_rtg_scrs_records.append((strat, k, x, y))

# create list of tuples for parameterization: [(RatingProvider, Rating, RatingScore), ]
# RatingScore is for "base" strategy
st_basestrat_prov_rtg_scrs_records = []
for (k, v_rtg, v_scores) in zip(
    st_rtg_prov_list, st_rtg_dict["base"].values(), st_scrs_dict["base"].values()
):
    for (x, y) in zip(v_rtg, v_scores):
        st_basestrat_prov_rtg_scrs_records.append((k, x, y))

# create long/tidy dataframe
st_rtg_df_long = pd.DataFrame.from_records(
    st_strat_prov_rtg_scrs_records,
    columns=["Strategy", "RatingProvider", "Rating", "RatingScore"],
)


def _convert_rtg_long_to_rtg_wide(strat: str) -> pd.DataFrame:
    out = pd.concat(
        [
            st_rtg_df_long.loc[
                (st_rtg_df_long["RatingProvider"] == rating_provider)
                & (st_rtg_df_long["Strategy"] == strat),
                "Rating",
            ]
            .reset_index(drop=True)
            .rename(rating_provider)
            for rating_provider in st_rtg_prov_list
        ],
        axis=1,
    )
    out.insert(0, "Strategy", strat)
    return out


# create wide dataframe with ratings in columns and strategies vertically stacked
st_rtg_df_wide = pd.concat(
    [_convert_rtg_long_to_rtg_wide(strat) for strat in st_strategies], axis=0
).reset_index(drop=True)


def _convert_scrs_long_to_rtg_wide(strat: str) -> pd.DataFrame:
    out = pd.concat(
        [
            st_rtg_df_long.loc[
                (st_rtg_df_long["RatingProvider"] == rating_provider)
                & (st_rtg_df_long["Strategy"] == strat),
                "RatingScore",
            ]
            .reset_index(drop=True)
            .rename(f"rtg_score_{rating_provider}")
            for rating_provider in st_rtg_prov_list
        ],
        axis=1,
    )
    out.insert(0, "Strategy", strat)
    return out


# create wide dataframe with scores in columns and strategies vertically stacked.
st_scores_df_wide = pd.concat(
    [_convert_scrs_long_to_rtg_wide(strat) for strat in st_strategies], axis=0
).reset_index(drop=True)

# create tuple of series [(Strategy, RatingProvider, RatingScore), ]
st_strat_prov_scores_rtg_series = [
    (
        strat,
        rating_provider,
        st_rtg_df_long.loc[
            (st_rtg_df_long["RatingProvider"] == rating_provider)
            & (st_rtg_df_long["Strategy"] == strat),
            "RatingScore",
        ]
        .reset_index(drop=True)
        .squeeze(),
        st_rtg_df_long.loc[
            (st_rtg_df_long["RatingProvider"] == rating_provider)
            & (st_rtg_df_long["Strategy"] == strat),
            "Rating",
        ]
        .reset_index(drop=True)
        .squeeze(),
    )
    for rating_provider in st_rtg_prov_list
    for strat in st_strategies
]

# create tuple of series [(RatingProvider, RatingScore), ]
st_basestrat_prov_scores_rtg_series = [
    (
        rating_provider,
        st_rtg_df_long.loc[
            (st_rtg_df_long["RatingProvider"] == rating_provider)
            & (st_rtg_df_long["Strategy"] == "base"),
            "RatingScore",
        ]
        .reset_index(drop=True)
        .squeeze(),
        st_rtg_df_long.loc[
            (st_rtg_df_long["RatingProvider"] == rating_provider)
            & (st_rtg_df_long["Strategy"] == "base"),
            "Rating",
        ]
        .reset_index(drop=True)
        .squeeze(),
    )
    for rating_provider in st_rtg_prov_list
]

# --- invalid dataframe ----------------------------------------------------------------
input_invalid_df = pd.DataFrame(
    data={
        "Fitch": [np.nan, "foo", -10],
        "DBRS": ["bar", 20_000, np.nan],
    }
)
exp_invalid_df = pd.DataFrame(
    data={
        "Fitch": [np.nan, np.nan, np.nan],
        "DBRS": [np.nan, np.nan, np.nan],
    }
)

# --- error message constant with respect to invalid rating provider -------------------
LT_ERR_MSG = (
    "'foo' is not a valid rating provider. 'rating_provider' must "
    "be in ['fitch', 'moody', 'sp', 's&p', 'dbrs', 'bloomberg', 'ice']."
)

ST_ERR_MSG = (
    "'foo' is not a valid rating provider. 'rating_provider' must "
    "be in ['fitch', 'moody', 'sp', 's&p', 'dbrs']."
)

# --- warf -----------------------------------------------------------------------------
warf_df_wide = pd.DataFrame(
    data=[
        [1, 1, 1, 1, 1],
        [10, 10, 10, 10, 10],
        [20, 20, 20, 20, 20],
        [40, 40, 40, 40, 40],
        [70, 70, 70, 70, 70],
        [120, 120, 120, 120, 120],
        [180, 180, 180, 180, 180],
        [260, 260, 260, 260, 260],
        [360, 360, 360, 360, 360],
        [610, 610, 610, 610, 610],
        [940, 940, 940, 940, 940],
        [1350, 1350, 1350, 1350, 1350],
        [1766, 1766, 1766, 1766, 1766],
        [2220, 2220, 2220, 2220, 2220],
        [2720, 2720, 2720, 2720, 2720],
        [3490, 3490, 3490, 3490, 3490],
        [4770, 4770, 4770, 4770, 4770],
        [6500, 6500, 6500, 6500, 6500],
        [8070, 8070, 8070, 8070, 8070],
        [9998, 9998, 9998, 9998, 9998],
        [9999, 9999, 9999, 9999, 9999],
        [10000, 10000, 10000, 10000, 10000],
    ],
    columns=lt_rtg_prov_list,
)
warf_df_long = pd.melt(warf_df_wide, var_name="rating_provider", value_name="warf")

warf_df_wide_with_err_row = pd.concat(
    [
        warf_df_wide,
        pd.DataFrame(
            data=[["foo", "foo", "foo", "foo", "foo"]],
            columns=warf_df_wide.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)
