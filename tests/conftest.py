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

# --- define inputs and expectations
rating_provider_lt_list = ["Fitch", "Moody", "SP", "Bloomberg", "DBRS", "ICE"]
rating_provider_st_list = ["Fitch", "Moody", "SP", "DBRS"]

# --- ratings --------------------------------------------------------------------------
# --- long-term
rtg_df_wide = pd.DataFrame(
    data=[
        ["AAA", "Aaa", "AAA", "AAA", "AAA", "AAA"],
        ["AA+", "Aa1", "AA+", "AA+", "AAH", "AA+"],
        ["AA", "Aa2", "AA", "AA", "AA", "AA"],
        ["AA-", "Aa3", "AA-", "AA-", "AAL", "AA-"],
        ["A+", "A1", "A+", "A+", "AH", "A+"],
        ["A", "A2", "A", "A", "A", "A"],
        ["A-", "A3", "A-", "A-", "AL", "A-"],
        ["BBB+", "Baa1", "BBB+", "BBB+", "BBBH", "BBB+"],
        ["BBB", "Baa2", "BBB", "BBB", "BBB", "BBB"],
        ["BBB-", "Baa3", "BBB-", "BBB-", "BBBL", "BBB-"],
        ["BB+", "Ba1", "BB+", "BB+", "BBH", "BB+"],
        ["BB", "Ba2", "BB", "BB", "BB", "BB"],
        ["BB-", "Ba3", "BB-", "BB-", "BBL", "BB-"],
        ["B+", "B1", "B+", "B+", "BH", "B+"],
        ["B", "B2", "B", "B", "B", "B"],
        ["B-", "B3", "B-", "B-", "BL", "B-"],
        ["CCC+", "Caa1", "CCC+", "CCC+", "CCCH", "CCC+"],
        ["CCC", "Caa2", "CCC", "CCC", "CCC", "CCC"],
        ["CCC-", "Caa3", "CCC-", "CCC-", "CCCL", "CCC-"],
        ["CC", "Ca", "CC", "CC", "CC", "CC"],
        ["C", "C", "C", "C", "C", "C"],
        ["D", "D", "D", "DDD", "D", "D"],
    ],
    columns=rating_provider_lt_list,
)
rtg_df_long = pd.melt(rtg_df_wide, var_name="rating_provider", value_name="rating")

rtg_df_wide_with_err_row = pd.concat(
    [
        rtg_df_wide,
        pd.DataFrame(
            data=[["foo", "foo", "foo", "foo", "foo", "foo"]],
            columns=rtg_df_wide.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)

rtg_df_wide_with_watch_unsolicited = pd.DataFrame(
    data=[
        ["AAA (Developing)", "Aaa", "AAA", "AAA", "AAA", "AAA"],
        ["AA+", "Aa1", "AA+", "AA+", "AAH", "AA+"],
        ["AA", "Aa2", "AA", "AA", "AA *-", "AA"],
        ["AA-", "Aa3", "AA-", "AA-", "AAL", "AA-"],
        ["A+", "A1", "A+", "A+", "AH", "A+"],
        ["A", "A2", "A", "A", "A", "A"],
        ["A-", "A3", "A-", "A-", "AL", "A-"],
        ["BBB+", "Baa1", "BBB+", "BBB+ (CwPositive)", "BBBH", "BBB+"],
        ["BBB", "Baa2", "BBB", "BBB", "BBB", "BBB"],
        ["BBB-", "Baa3", "BBB- *-", "BBB-", "BBBL", "BBB-"],
        ["BB+", "Ba1", "BB+U", "BB+", "BBH", "BB+"],
        ["BB", "Ba2", "BB", "BB", "BB", "BB"],
        ["BB-", "Ba3", "BB-", "BB-u", "BBL", "BB-u"],
        ["B+", "B1", "B+", "B+", "BH", "B+"],
        ["B", "B2", "B", "B", "B", "B"],
        ["B-", "B3", "B-", "B-", "BL", "B-"],
        ["CCC+", "Caa1", "CCC+", "CCC+", "CCCH", "CCC+"],
        ["CCC", "Caa2", "CCCu", "CCC", "CCC", "CCC"],
        ["CCC-", "Caa3u", "CCC-", "CCC-", "CCCL", "CCC-"],
        ["CCu", "Ca", "CC", "CC", "CC", "CC"],
        ["C", "C", "C", "C", "C", "C"],
        ["D", "D", "D", "DDD", "D", "D"],
    ],
    columns=rating_provider_lt_list,
)
rtg_df_long_with_watch_unsolicited = pd.melt(
    rtg_df_wide_with_watch_unsolicited, var_name="rating_provider", value_name="rating"
)

# --- short-term
rtg_df_wide_st = pd.DataFrame(
    data=[
        ["F1+", "P-1", "A-1+", "R-1 (high)"],
        [np.nan, np.nan, np.nan, "R-1 (mid)"],
        [np.nan, np.nan, np.nan, "R-1 (low)"],
        ["F1", np.nan, "A-1", "R-2 (high)"],
        [np.nan, np.nan, np.nan, "R-2 (mid)"],
        ["F2", "P-2", "A-2", "R-2 (low)"],
        [np.nan, np.nan, np.nan, "R-3 (high)"],
        ["F3", "P-3", "A-3", "R-3 (mid)"],
        [np.nan, np.nan, np.nan, "R-3 (low)"],
        [np.nan, "NP", "B", "R-4"],
        [np.nan, np.nan, np.nan, "R-5"],
        [np.nan, np.nan, "C", np.nan],
        [np.nan, np.nan, "D", np.nan],
    ],
    columns=rating_provider_st_list,
)

rtg_df_long_st = pd.melt(
    rtg_df_wide_st, var_name="rating_provider", value_name="rating"
).dropna()

rtg_df_wide_st_with_err_row = pd.concat(
    [
        rtg_df_wide_st,
        pd.DataFrame(
            data=[["foo", "foo", "foo", "foo"]],
            columns=rtg_df_wide_st.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)


# --- scores ---------------------------------------------------------------------------
# --- long-term
scores_df_wide = pd.DataFrame(
    data=[
        [1, 1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3, 3],
        [4, 4, 4, 4, 4, 4],
        [5, 5, 5, 5, 5, 5],
        [6, 6, 6, 6, 6, 6],
        [7, 7, 7, 7, 7, 7],
        [8, 8, 8, 8, 8, 8],
        [9, 9, 9, 9, 9, 9],
        [10, 10, 10, 10, 10, 10],
        [11, 11, 11, 11, 11, 11],
        [12, 12, 12, 12, 12, 12],
        [13, 13, 13, 13, 13, 13],
        [14, 14, 14, 14, 14, 14],
        [15, 15, 15, 15, 15, 15],
        [16, 16, 16, 16, 16, 16],
        [17, 17, 17, 17, 17, 17],
        [18, 18, 18, 18, 18, 18],
        [19, 19, 19, 19, 19, 19],
        [20, 20, 20, 20, 20, 20],
        [21, 21, 21, 21, 21, 21],
        [22, 22, 22, 22, 22, 22],
    ],
    columns=rating_provider_lt_list,
)
scores_df_long = pd.melt(
    scores_df_wide, var_name="rating_provider", value_name="rtg_score"
)

scores_df_wide_with_err_row = pd.concat(
    [
        scores_df_wide,
        pd.DataFrame(
            data=[["foo", "foo", "foo", "foo", "foo", "foo"]],
            columns=scores_df_wide.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)

# --- short-term
scores_df_wide_st = pd.DataFrame(
    data=[
        [1, 1, 1, 1],
        [np.nan, np.nan, np.nan, 2],
        [np.nan, np.nan, np.nan, 3],
        [5, np.nan, 5, 5],
        [np.nan, np.nan, np.nan, 6],
        [7, 7, 7, 7],
        [np.nan, np.nan, np.nan, 8],
        [9, 9, 9, 9],
        [np.nan, np.nan, np.nan, 10],
        [np.nan, 12, 12, 12],
        [np.nan, np.nan, np.nan, 15],
        [np.nan, np.nan, 18, np.nan],
        [np.nan, np.nan, 22, np.nan],
    ],
    columns=rating_provider_st_list,
)
scores_df_long_st = pd.melt(
    scores_df_wide_st, var_name="rating_provider", value_name="rtg_score"
).dropna()
scores_df_long_st["rtg_score"] = scores_df_long_st["rtg_score"].astype(np.int64)

scores_df_wide_st_with_err_row = pd.concat(
    [
        scores_df_wide_st,
        pd.DataFrame(
            data=[["foo", "foo", "foo", "foo"]], columns=scores_df_wide_st.columns
        ),
    ],
    axis=0,
    ignore_index=True,
)

# --- warf -----------------------------------------------------------------------------
warf_df_wide = pd.DataFrame(
    data=[
        [1, 1, 1, 1, 1, 1],
        [10, 10, 10, 10, 10, 10],
        [20, 20, 20, 20, 20, 20],
        [40, 40, 40, 40, 40, 40],
        [70, 70, 70, 70, 70, 70],
        [120, 120, 120, 120, 120, 120],
        [180, 180, 180, 180, 180, 180],
        [260, 260, 260, 260, 260, 260],
        [360, 360, 360, 360, 360, 360],
        [610, 610, 610, 610, 610, 610],
        [940, 940, 940, 940, 940, 940],
        [1350, 1350, 1350, 1350, 1350, 1350],
        [1766, 1766, 1766, 1766, 1766, 1766],
        [2220, 2220, 2220, 2220, 2220, 2220],
        [2720, 2720, 2720, 2720, 2720, 2720],
        [3490, 3490, 3490, 3490, 3490, 3490],
        [4770, 4770, 4770, 4770, 4770, 4770],
        [6500, 6500, 6500, 6500, 6500, 6500],
        [8070, 8070, 8070, 8070, 8070, 8070],
        [9998, 9998, 9998, 9998, 9998, 9998],
        [9999, 9999, 9999, 9999, 9999, 9999],
        [10000, 10000, 10000, 10000, 10000, 10000],
    ],
    columns=rating_provider_lt_list,
)
warf_df_long = pd.melt(warf_df_wide, var_name="rating_provider", value_name="warf")

warf_df_wide_with_err_row = pd.concat(
    [
        warf_df_wide,
        pd.DataFrame(
            data=[["foo", "foo", "foo", "foo", "foo", "foo"]],
            columns=warf_df_wide.columns,
        ),
    ],
    axis=0,
    ignore_index=True,
)

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
ERR_MSG = (
    "'foo' is not a valid rating provider. 'rating_provider' must "
    "be in ['Moody', 'SP', 'Fitch', 'Bloomberg', 'DBRS', 'ICE']."
)

# --- params ---------------------------------------------------------------------------
params_provider_scores_ratings_lt = [
    (
        rating_provider,
        scores_df_long.loc[
            scores_df_long["rating_provider"] == rating_provider,
            "rtg_score",
        ]
        .reset_index(drop=True)
        .squeeze(),
        rtg_df_long.loc[
            rtg_df_long["rating_provider"] == rating_provider,
            ["rating"],
        ]
        .reset_index(drop=True)
        .squeeze(),
    )
    for rating_provider in rating_provider_lt_list
]

params_provider_scores_ratings_st = [
    (
        rating_provider,
        scores_df_long_st.loc[
            scores_df_long_st["rating_provider"] == rating_provider,
            "rtg_score",
        ]
        .reset_index(drop=True)
        .squeeze(),
        rtg_df_long_st.loc[
            rtg_df_long_st["rating_provider"] == rating_provider,
            ["rating"],
        ]
        .reset_index(drop=True)
        .squeeze(),
    )
    for rating_provider in rating_provider_st_list
]

params_provider_warf_ratings = [
    (
        rating_provider,
        warf_df_long.loc[
            scores_df_long["rating_provider"] == rating_provider,
            "warf",
        ]
        .reset_index(drop=True)
        .squeeze(),
        rtg_df_long.loc[
            rtg_df_long["rating_provider"] == rating_provider,
            ["rating"],
        ]
        .reset_index(drop=True)
        .squeeze(),
    )
    for rating_provider in rating_provider_lt_list
]

params_provider_ratings_warf = [
    (
        rating_provider,
        rtg_df_long.loc[
            rtg_df_long["rating_provider"] == rating_provider,
            ["rating"],
        ]
        .reset_index(drop=True)
        .squeeze(),
        warf_df_long.loc[
            warf_df_long["rating_provider"] == rating_provider,
            "warf",
        ]
        .reset_index(drop=True)
        .squeeze(),
    )
    for rating_provider in rating_provider_lt_list
]
