# pyratings — Working with credit ratings, professionally and efficiently
  
![img](https://img.shields.io/pypi/v/pyratings) ![img](https://img.shields.io/pypi/pyversions/pyratings) ![img](https://img.shields.io/github/license/hsbc/pyratings) ![img](https://img.shields.io/github/issues/hsbc/pyratings) ![img](https://img.shields.io/github/stars/hsbc/pyratings) ![img](https://img.shields.io/badge/code%20style-black-black)

**Documentation**: [https://hsbc.github.io/pyratings/](https://hsbc.github.io/pyratings/)

**Source Code**: [https://github.com/hsbc/pyratings/](https://github.com/hsbc/pyratings/)

---

## What is it all about?
Do you work in the investment industry?
Do you work with fixed income instruments, such as bonds and credit securities?
Then you are probably concerned with credit ratings, too?

This Python library will be useful for portfolio managers, credit analysts, as well 
as anybody who is working with credit ratings.
It provides functions, which will be helpful in order to work with ratings in 
a professional and efficient way.

## Table of contents
- [What has _pyratings_ to offer and how might it help you?](#what-has-pyratings-to-offer-and-how-might-it-help-you)
- [How to install _pyratings_?](#how-to-install-pyratings)
- [Getting started with _pyratings_](#getting-started-with-pyratings)
    - [Cleaning ratings](#cleaning-ratings)
    - [Consolidating ratings](#consolidating-ratings)
    - [Translating ratings](#translating-ratings)
- [Support](#support)
- [Contributing](#contributing)
- [Acknowlegdements](#acknowledgements)
- [License](#license)


## What has _pyratings_ to offer and how might it help you?
Do you need to compute the average credit rating of an investment portfolio?
Do you need to compute the worst rating for individual securities', given these 
securities have ratings attached from more than one rating agency?
Do you need to compute the Weighted Average Rating Factor (WARF)?

If yes, you might want to take a look at **pyratings** and its offerings in the credit 
ratings space.

**pyratings** offers the following capabilities:

- Cleaning ratings for further processing, e.g. stripping off of rating watches.
- Transform long- and short-term ratings into rating scores and vice versa.
- Compute the best/second best/worst ratings on a security level basis within a
  portfolio context.
- Compute average ratings/rating scores on a portfolio level.
- Compute Weighted Average Rating Factor (WARF) on a portfolio level.
- Compute WARF buffer, i.e. distance from current WARF to the next maxWARF.

**pyratings** supports 
[long-term ratings](https://hsbc.github.io/pyratings/long_term_ratings) as well as 
[short-term ratings](https://hsbc.github.io/pyratings/short_term_ratings).
Currently, the following rating agencies will be supported:

- Moody's (long-term / short-term)
- Standard & Poors (long-term / short-term)
- Fitch (long-term / short-term)
- DBRS Morningstar (long-term / short-term)
- Bloomberg (long-term)


## How to install _pyratings_?
**pyratings** is listed on [pypi](https://pypi.org/project/pyratings/).
Make sure to have Python 3.9+ installed on your machine.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install **pyratings**.

```bash
pip install pyratings
```

You can also use [poetry](https://python-poetry.org/).

```bash
poetry add pyratings
```

## Getting started with _pyratings_
Here are some very basic code snippets to get you up and running.

### Cleaning ratings
Sometimes, a rating has a credit watch or an outlook attached to it.
In order to work with this rating, it is usually necessary to get rid of it.

```bash
>>> import pyratings as rtg

>>> rtg.get_pure_ratings("AA- *+")
"AA-"
```
Cleaning a pandas datraframe, which comprises several securities with ratings from S&P 
and Fitch:

```bash
>>> import numpy as np
>>> import pandas as pd

>>> import pyratings as rtg


>>> rtg_df = pd.DataFrame(
...    data={
...        "rtg_SP": [
...            "BB+ *-",
...            "BBB *+",
...            np.nan,
...            "AA- (Developing)",
...            np.nan,
...            "CCC+ (CwPositive)",
...            "BB+u",
...        ],
...        "rtg_Fitch": [
...            "BB+ *-",
...            "BBB *+",
...            np.nan,
...            "AA- (Developing)",
...            np.nan,
...            "CCC+ (CwPositive)",
...            "BB+u",
...        ],
...    },
... )
  
>>> rtg_df
              rtg_SP          rtg_Fitch
0             BB+ *-             BB+ *-
1             BBB *+             BBB *+
2                NaN                NaN
3   AA- (Developing)   AA- (Developing)
4                NaN                NaN
5  CCC+ (CwPositive)  CCC+ (CwPositive)
6               BB+u               BB+u

# Get rid of all the noise.

>>> rtg.get_pure_ratings(rtg_df)
  rtg_SP_clean rtg_Fitch_clean
0          BB+             BB+
1          BBB             BBB
2          NaN             NaN
3          AA-             AA-
4          NaN             NaN
5         CCC+            CCC+
6          BB+             BB+
```

### Consolidating ratings
It is quite common that an individual credit security has been rated by several 
credit agencies.
In this case, you may want to compute the best or worst rating. 

```bash
>>> import pandas as pd

>>> import pyratings as rtg

>>> ratings_df = pd.DataFrame(
...     data=(
...         {
...             "rating_S&P": ['AAA', 'AA-', 'AA+', 'BB-', 'C'],
...             "rating_Moody": ['Aa1', 'Aa3', 'Aa2', 'Ba3', 'Ca'],
...             "rating_Fitch": ['AA-', 'AA-', 'AA-', 'B+', 'C'],
...         }
...     )
... )
  
>>>  ratings_df
  rating_S&P rating_Moody rating_Fitch
0        AAA          Aa1          AA-
1        AA-          Aa3          AA-
2        AA+          Aa2          AA-
3        BB-          Ba3           B+
4          C           Ca            C

# Return a pd.Series with the worst ratings.

>>> rtg.get_worst_ratings(
...   ratings_df, rating_provider_input=["S&P", "Moody", "Fitch"]
... )
0    AA-
1    AA-
2    AA-
3     B+
4      C
Name: worst_rtg, dtype: object
```

### Translating ratings
To work with ratings, it's sometimes necessary to translate human-readable ratings 
into numerical rating scores and vice versa.
**pyratings** offers a number of functions on that front.

The [documentation](https://hsbc.github.io/pyratings/user_guide/translation) shows 
in detail how **pyratings** translates human-readable ratings into numerical rating 
scores.<br>
Here's an example how to translate a pandas series from ratings to scores and vice 
versa. 

```bash
>>> import pandas as pd

>>> import pyratings as rtg


>>> ratings_series = pd.Series(
...     data=["Baa1", "C", "NR", "WD", "D", "B1", "SD"], name='Moody'
... )
>>> scores_series = rtg.get_scores_from_ratings(
...     ratings=ratings_series, rating_provider="Moody's", tenor="long-term"
... )
>>> scores_series
0     8.0
1    21.0
2     NaN
3     NaN
4    22.0
5    14.0
6    22.0
Name: rtg_score_Moody, dtype: float64

# Translate these rating scores back, but this time use DBRS' rating scale

>>> rtg.get_ratings_from_scores(
...     rating_scores=scores_series, rating_provider="DBRS", tenor="long-term"
... )
0    BBBH
1       C
2     NaN
3     NaN
4       D
5      BH
6       D
Name: rtg_DBRS, dtype: object
```


## Support
If you need help or have any questions, the first step should be to take a look at the 
[docs](https://hsbc.github.io/pyratings/).
If you can't find an answer, please open an issue on 
[GitHub](https://github.com/hsbc/pyratings//issues/new), or send an email to 
<opensource@hsbc.de>.
The subject line should contain '#pyratings'


## Contributing
We very much welcome contributions!
Before you begin, please read our 
[contributing guideliens](https://hsbc.github.io/pyratings/contributing/).


## Acknowledgements
Thanks to

- [Andreas Vester](https://github.com/a-vester), project creator and lead developer
- [Deepak Parashar](https://github.com/deepakparashar1987), for their help with 
  testing the code and working on all kinds of PRs.
- [Sander Cohen](https://github.com/sander2825), for their help to improve the 
  documentation as well as the intense discussion on how to best implement 
  short-term ratings into the project.
- [Marco Erling](https://github.com/MarcoGER), for actively participating in 
  discussions on how to best incorporate short-term ratings.
- [Thomas Steenbergen](https://github.com/tsteenbe), for their
  [code contribution](https://github.com/hsbc/pyratings/pull/1) regarding the 
  improvement of metadata in setup.py.
- [Ekow Folson](https://github.com/MEFolson), for their help of setting up this 
  repository and make it possible to become the very first open source contribution 
  from [HSBC](https://github.com/hsbc).


## License
This project is licensed under the Apache 2.0 License – please see the
[LICENSE](https://hsbc.github.io/pyratings/license) file.
